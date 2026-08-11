"""
Evidence Fusion Engine

Fuses evidence from four independent streams:
    1. Graph Evidence (Knowledge Graph traversal paths)
    2. AST Evidence (Structural parser output)
    3. Semantic Evidence (UIR symbol table)
    4. Documentation Evidence (Extracted claims & context)

Pipeline:
    Graph Evidence
    AST Evidence       →  Deduplication → Evidence Ranking → Unified EvidenceContext
    Semantic Evidence
    Doc Evidence

Architecture position: Evidence Retrieval → Evidence Fusion → Evidence Validation → Reasoning
"""
import uuid
from typing import List, Dict, Tuple
from dataclasses import dataclass, field

from app.models.knowledge.evidence import (
    EvidenceChain, EvidenceItem, EvidenceSource, EvidenceStrength, EvidenceContext
)
from app.models.claim import Claim


@dataclass
class FusionStream:
    name: str          # "graph" | "ast" | "semantic" | "documentation"
    chains: List[EvidenceChain] = field(default_factory=list)
    weight: float = 1.0


@dataclass
class FusionResult:
    fused_chains: List[EvidenceChain] = field(default_factory=list)
    deduplicated_count: int = 0
    stream_contributions: Dict[str, int] = field(default_factory=dict)
    diversity_score: float = 0.0
    aggregate_ranking_score: float = 0.0


# Stream weights: how strongly each evidence source contributes to overall
# confidence
STREAM_WEIGHTS = {
    "graph": 0.90,   # Graph traversal paths — strongest evidence
    "ast": 0.80,   # AST parser output — structural
    "semantic": 0.75,   # UIR semantic symbols — contextual
    "documentation": 0.60,   # Documentation claims — weakest alone
}


class EvidenceFusionEngine:
    """
    Fuses, deduplicates, and ranks evidence from all four independent streams.
    Produces a single, unified EvidenceContext for the Reasoning Engine.
    """

    def fuse(
        self,
        graph_chains: List[EvidenceChain],
        ast_chains: List[EvidenceChain],
        semantic_chains: List[EvidenceChain],
        doc_chains: List[EvidenceChain],
        claim: Claim,
    ) -> Tuple[EvidenceContext, FusionResult]:
        """
        Main fusion pipeline:
        Graph + AST + Semantic + Documentation → Deduplication → Ranking → Unified Context
        """
        streams = [
            FusionStream("graph", graph_chains, STREAM_WEIGHTS["graph"]),
            FusionStream("ast", ast_chains, STREAM_WEIGHTS["ast"]),
            FusionStream(
                "semantic",
                semantic_chains,
                STREAM_WEIGHTS["semantic"]),
            FusionStream(
                "documentation",
                doc_chains,
                STREAM_WEIGHTS["documentation"]),
        ]

        # Step 1: Collect and tag chains by stream
        all_chains: List[EvidenceChain] = []
        stream_contributions: Dict[str, int] = {}
        for stream in streams:
            for chain in stream.chains:
                # Apply stream weight to ranking score
                chain.ranking_score = round(
                    chain.ranking_score * stream.weight, 4)
            all_chains.extend(stream.chains)
            stream_contributions[stream.name] = len(stream.chains)

        # Step 2: Deduplicate by graph_path + code snippet fingerprint
        deduplicated, removed = self._deduplicate(all_chains)

        # Step 3: Rank deduplicated chains
        ranked = self._rank(deduplicated)

        # Step 4: Compute diversity (how many streams contributed)
        active_streams = sum(1 for v in stream_contributions.values() if v > 0)
        diversity_score = round(active_streams / len(STREAM_WEIGHTS), 4)

        # Step 5: Aggregate ranking
        agg_ranking = round(
            sum(c.ranking_score for c in ranked) / max(len(ranked), 1), 4
        )

        fusion_result = FusionResult(
            fused_chains=ranked,
            deduplicated_count=removed,
            stream_contributions=stream_contributions,
            diversity_score=diversity_score,
            aggregate_ranking_score=agg_ranking,
        )

        # Step 6: Build unified EvidenceContext
        from app.models.knowledge.evidence import EvidenceCandidate
        candidates = []
        for chain in ranked:
            for item in chain.sequence:
                candidates.append(EvidenceCandidate(
                    source_engine=chain.retrieval_strategy,
                    content=item.code_snippet,
                    file_path=item.source.file_path,
                    content_snippet=item.code_snippet,
                    metadata={
                        "chain_id": chain.chain_id,
                        "graph_path": chain.graph_path,
                        "ranking_score": chain.ranking_score,
                        "feature": chain.chain_type,
                    },
                    chain=chain,
                ))

        context = EvidenceContext(
            claim=claim,
            candidates=candidates,
            chains=ranked)
        return context, fusion_result

    # ─── Internal algorithms ────────────────────────────────────────────────

    def _deduplicate(
            self, chains: List[EvidenceChain]) -> Tuple[List[EvidenceChain], int]:
        """
        Removes duplicate chains by graph_path + snippet fingerprint.
        Keeps the chain with the highest ranking_score when duplicates exist.
        """
        seen: Dict[str, EvidenceChain] = {}
        for chain in chains:
            # Fingerprint based on structural identity, not content
            snippets = "|".join(
                item.code_snippet[:60].lower() for item in chain.sequence
            )
            fingerprint = f"{chain.graph_path}::{snippets}"

            existing = seen.get(fingerprint)
            if existing is None or chain.ranking_score > existing.ranking_score:
                seen[fingerprint] = chain

        deduplicated = list(seen.values())
        return deduplicated, len(chains) - len(deduplicated)

    def _rank(self, chains: List[EvidenceChain]) -> List[EvidenceChain]:
        """
        Ranks evidence chains by:
            1. ranking_score (primary)
            2. sequence length (tie-break — more evidence items = more complete)
            3. graph_path length (tie-break — deeper traversal = stronger)
        """
        return sorted(
            chains,
            key=lambda c: (
                c.ranking_score, len(
                    c.sequence), len(
                    c.graph_path)),
            reverse=True,
        )

    def build_doc_chains(
            self, doc_texts: List[str], claim: Claim) -> List[EvidenceChain]:
        """
        Constructs minimal EvidenceChains from raw documentation text.
        Used when no structured graph evidence is available for claims.
        """
        chains = []
        for text in doc_texts:
            if not text.strip():
                continue
            source = EvidenceSource(
                file_path="README.md",
                parser_used="DocumentParser")
            item = EvidenceItem(
                source=source,
                node_type="Statement",
                context_type="documentation",
                code_snippet=text[:200],
                evidence_strength=EvidenceStrength.SUPPORTING,
            )
            chains.append(EvidenceChain(
                chain_id=str(uuid.uuid4()),
                chain_type="Documentation Claim",
                retrieval_strategy="Documentation",
                sequence=[item],
                graph_path="README → Statement",
                ranking_score=0.6 * STREAM_WEIGHTS["documentation"],
                reasoning_trace=f"Documentation states: {text[:100]}",
            ))
        return chains
