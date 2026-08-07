"""
Evidence Quality Assessment

Classifies each EvidenceChain as PRIMARY / SECONDARY / SUPPORTING and
computes a deterministic quality score that feeds directly into the Trust Scorer.

Architecture position: Evidence Validation → Evidence Quality Assessment → Trust Score

Quality Score Formula:
    quality_score = (strength_weight × 0.50)
                  + (completeness × 0.30)
                  + (provenance_richness × 0.20)
"""
from typing import List
from dataclasses import dataclass

from app.models.knowledge.evidence import EvidenceChain, EvidenceStrength


@dataclass
class EvidenceQualityResult:
    chain_id: str
    classification: EvidenceStrength
    quality_score: float           # 0.0 – 1.0
    strength_weight: float
    completeness_score: float
    provenance_richness: float
    quality_label: str             # "Strong" | "Medium" | "Weak"


class EvidenceQualityAssessor:
    """
    Assesses evidence quality before it enters the Trust Scorer.
    Replaces arbitrary quality values with a deterministic, model-driven score.
    """

    # Strength weights map: node type → weight (mirrors ranking formula)
    NODE_TYPE_WEIGHTS = {
        "Annotation": 1.0,
        "Import":     0.8,
        "Method":     0.7,
        "Class":      0.75,
        "Interface":  0.75,
        "Variable":   0.5,
        "Comment":    0.2,
        "unknown":    0.4,
    }

    STRENGTH_WEIGHTS = {
        EvidenceStrength.PRIMARY:    1.0,
        EvidenceStrength.SECONDARY:  0.7,
        EvidenceStrength.SUPPORTING: 0.4,
    }

    def assess(self, chain: EvidenceChain) -> EvidenceQualityResult:
        """
        Compute a deterministic quality score for a single EvidenceChain.
        """
        # 1. Strength Weight — average over items in the chain
        if chain.sequence:
            raw_weights = [
                self.NODE_TYPE_WEIGHTS.get(item.node_type, 0.4)
                for item in chain.sequence
            ]
            strength_weight = sum(raw_weights) / len(raw_weights)
        else:
            strength_weight = 0.1

        # 2. Completeness — how many fields are populated in items
        completeness_score = self._compute_completeness(chain)

        # 3. Provenance Richness — how many source fields are non-default
        provenance_richness = self._compute_provenance_richness(chain)

        # 4. Final Quality Score
        quality_score = round(
            (strength_weight * 0.50) +
            (completeness_score * 0.30) +
            (provenance_richness * 0.20),
            4
        )

        # 5. Classification
        classification = self._classify(chain, quality_score)

        # 6. Human-readable label
        if quality_score >= 0.75:
            quality_label = "Strong"
        elif quality_score >= 0.45:
            quality_label = "Medium"
        else:
            quality_label = "Weak"

        return EvidenceQualityResult(
            chain_id=chain.chain_id,
            classification=classification,
            quality_score=quality_score,
            strength_weight=strength_weight,
            completeness_score=completeness_score,
            provenance_richness=provenance_richness,
            quality_label=quality_label,
        )

    def assess_all(self, chains: List[EvidenceChain]) -> List[EvidenceQualityResult]:
        return [self.assess(chain) for chain in chains]

    def aggregate_quality(self, results: List[EvidenceQualityResult]) -> float:
        """
        Returns the aggregated quality score for a set of evidence chains.
        Used as the `evidence_quality` input to TrustScorer.
        """
        if not results:
            return 0.0
        return round(sum(r.quality_score for r in results) / len(results), 4)

    # ─── Internal helpers ─────────────────────────────────────────────────────

    def _compute_completeness(self, chain: EvidenceChain) -> float:
        """Ratio of non-empty/non-default fields across all items."""
        if not chain.sequence:
            return 0.0
        scores = []
        for item in chain.sequence:
            filled = sum([
                item.node_type not in ("", "unknown"),
                item.symbol not in ("", "unknown"),
                item.qualified_name not in ("", "unknown"),
                item.code_snippet != "",
                item.graph_node_id is not None,
            ])
            scores.append(filled / 5.0)
        return round(sum(scores) / len(scores), 4)

    def _compute_provenance_richness(self, chain: EvidenceChain) -> float:
        """Ratio of non-default source fields across all items."""
        if not chain.sequence:
            return 0.0
        scores = []
        for item in chain.sequence:
            src = item.source
            filled = sum([
                src.file_path not in ("", "Unknown", "unknown"),
                src.line_number is not None,
                src.language not in ("", "unknown"),
                src.parser_used not in ("", "unknown"),
                src.commit_sha not in ("", "HEAD"),
            ])
            scores.append(filled / 5.0)
        return round(sum(scores) / len(scores), 4)

    def _classify(self, chain: EvidenceChain, quality_score: float) -> EvidenceStrength:
        """Classify the chain as PRIMARY / SECONDARY / SUPPORTING."""
        # A chain with high graph coverage and a strong ranking score is PRIMARY
        has_graph_path = bool(chain.graph_path and chain.graph_path != "")
        has_high_rank = chain.ranking_score >= 0.8
        if has_graph_path and has_high_rank and quality_score >= 0.7:
            return EvidenceStrength.PRIMARY
        elif quality_score >= 0.45:
            return EvidenceStrength.SECONDARY
        return EvidenceStrength.SUPPORTING
