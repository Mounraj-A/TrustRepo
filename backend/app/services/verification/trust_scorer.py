"""
Trust Scorer — Formal Multi-Factor Trust Score Calculation

Formal definition:
    TrustScore = Σ(wᵢ × metricᵢ) − Σ(penaltyⱼ)

Claim-Level Metrics (wᵢ):
    m₁ = Evidence Quality        (w=0.25)
    m₂ = Evidence Diversity      (w=0.20)
    m₃ = Verification Confidence (w=0.30)
    m₄ = Feature Coverage        (w=0.25)
    ─────────────────────────────────────
    Metric Sum = 100 points max

Claim-Level Penalties:
    p₁ = Contradiction Penalty   (−20 pts)
    p₂ = No Evidence Penalty     (−30 pts)

Repository-Level Metrics (used in ReportGenerator):
    M₁ = Documentation Coverage  (w=0.30)
    M₂ = Avg Evidence Quality    (w=0.25)
    M₃ = Verification Rate       (w=0.25)
    M₄ = Claim Coverage          (w=0.20)

Repository-Level Penalties:
    P₁ = Contradiction Rate       (−10 pts each)
    P₂ = Missing Documentation    (−5 pts each)
    P₃ = Dead/False Documentation (−7 pts each)
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.knowledge.investigation import VerificationVerdict


class TrustScorer:
    """
    Implements the formal TrustScore = Σ(wᵢ × metricᵢ) − Σ(penaltyⱼ) formula
    for both claim-level and repository-level scoring.
    """

    # ── Claim-Level Weights ─────────────────────────────────────────────────
    CLAIM_WEIGHTS = {
        "evidence_quality": 0.25,
        "evidence_diversity": 0.20,
        "verification_confidence": 0.30,
        "feature_coverage": 0.25,
    }

    # ── Claim-Level Penalties ───────────────────────────────────────────────
    CONTRADICTION_PENALTY = 20.0
    NO_EVIDENCE_PENALTY = 30.0

    # ── Repository-Level Weights ────────────────────────────────────────────
    REPO_WEIGHTS = {
        "documentation_coverage": 0.30,
        "avg_evidence_quality": 0.25,
        "verification_rate": 0.25,
        "claim_coverage": 0.20,
    }

    # ── Repository-Level Penalties ──────────────────────────────────────────
    CONTRADICTION_REPO_PENALTY = 10.0   # per contradiction
    MISSING_DOC_PENALTY = 5.0           # per missing documented feature
    FALSE_DOC_PENALTY = 7.0             # per dead/false documentation claim

    def calculate_claim_score(
        self,
        verdict: "VerificationVerdict",
        # list of dicts with source_weight, evidence_quality, parser_confidence
        evidence_sources: list,
        graph_connectivity: float,
        agreement_score: float,
        freshness_score: float,
        conflict_count: int
    ) -> float:
        """
        Claim-Level: Confidence = Σ(SourceWeight × EvidenceQuality × ParserConfidence)
                     × GraphConnectivity × AgreementScore × FreshnessScore ÷ ConflictPenalty
        """
        sigma_evidence = 0.0
        for ev in evidence_sources:
            sw = ev.get("source_weight", 1.0)
            eq = ev.get("evidence_quality", 0.5)
            pc = ev.get("parser_confidence", 1.0)
            sigma_evidence += (sw * eq * pc)

        if sigma_evidence == 0:
            sigma_evidence = 0.1  # prevent zero multiplication if no evidence

        conflict_penalty = max(1.0, conflict_count * 1.5)

        raw_score = (
            sigma_evidence *
            max(graph_connectivity, 0.1) *
            max(agreement_score, 0.1) *
            max(freshness_score, 0.1)
        ) / conflict_penalty

        # Normalize to 0-100
        normalized = min(raw_score * 100.0, 100.0)

        if len(evidence_sources) == 0:
            normalized -= self.NO_EVIDENCE_PENALTY

        return round(max(normalized, 0.0), 2)

    def calculate_repository_score(
        self,
        doc_score: float,
        tech_score: float,
        feature_score: float,
        capability_score: float,
        architecture_score: float,
        evidence_score: float,
        verification_score: float,
        graph_score: float
    ) -> float:
        """
        Enterprise-Grade Repository Trust Score calculation.
        Aggregates the multi-dimensional scores computed by individual authoritative engines.
        """
        weights = {
            "doc": 0.20,
            "tech": 0.10,
            "feature": 0.15,
            "capability": 0.10,
            "architecture": 0.10,
            "evidence": 0.15,
            "verification": 0.15,
            "graph": 0.05
        }

        raw_score = (
            (doc_score * weights["doc"]) +
            (tech_score * weights["tech"]) +
            (feature_score * weights["feature"]) +
            (capability_score * weights["capability"]) +
            (architecture_score * weights["architecture"]) +
            (evidence_score * weights["evidence"]) +
            (verification_score * weights["verification"]) +
            (graph_score * weights["graph"])
        )

        return round(max(min(raw_score, 100.0), 0.0), 2)

    # Backward-compatible alias (used by old callers)
    def calculate_score(self, investigation, verdict) -> float:
        evidence_count = len(investigation.evidence_context.candidates)
        from app.models.knowledge.investigation import VerificationVerdict
        # Map old signature to new formula inputs for backwards compatibility
        evidences = [{"source_weight": 1.0, "evidence_quality": 0.5,
                      "parser_confidence": investigation.confidence} for _ in range(evidence_count)]

        return self.calculate_claim_score(
            verdict=verdict,
            evidence_sources=evidences,
            graph_connectivity=0.8,
            agreement_score=0.9,
            freshness_score=1.0,
            conflict_count=1 if verdict == VerificationVerdict.CONTRADICTION else 0
        )
