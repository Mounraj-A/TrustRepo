"""
Verification Engine — explicit reasoning stages for dissertation-grade transparency.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import List, Tuple, TYPE_CHECKING

from app.models.knowledge.investigation import VerificationResult, VerificationVerdict
from app.models.knowledge.evidence import EvidenceChain
from app.services.verification.trust_scorer import TrustScorer
from app.services.verification.reasoning_agent import ReasoningAgent

if TYPE_CHECKING:
    from app.services.agents.base_agent import AgentMessage
    from app.services.analysis.claim_normalization_layer import NormalizedClaim


class VerificationEngine:
    """
    Produces an immutable VerificationResult with a full, explainable reasoning trace.
    Delegates deterministic reasoning to the ReasoningAgent.
    """

    def __init__(self):
        self.scorer = TrustScorer()
        self.reasoning_agent = ReasoningAgent()

    def verify(
        self,
        normalized_claim: "NormalizedClaim",
        agent_message: "AgentMessage"
    ) -> VerificationResult:
        
        # In a full system, we would extract EvidenceChains from the agent_message
        # For this prototype integration, if there are chains in the payload, use them.
        chains = []
        raw_chains = agent_message.payload.get("evidence_chains", [])
        for rc in raw_chains:
            try:
                chains.append(EvidenceChain(**rc))
            except Exception:
                pass
                
        # Fallback if no chains, mock a basic chain based on candidates
        if not chains:
            raw_candidates = agent_message.payload.get("fused_evidence", [])
            for rc in raw_candidates:
                from app.models.knowledge.evidence import EvidenceItem, EvidenceSource
                source = EvidenceSource(file_path=rc.get("file_path", "unknown"))
                item = EvidenceItem(source=source, code_snippet=rc.get("content", ""))
                chains.append(EvidenceChain(
                    chain_id="fallback",
                    sequence=[item],
                    reasoning_trace=f"Found '{rc.get('feature', 'evidence')}'",
                    ranking_score=0.8
                ))
        
        # ── Reasoning Agent ────────────────────────────────────────────────────
        from app.models.claim import Claim
        dummy_claim = Claim(id=normalized_claim.claim_id, text=normalized_claim.raw_text, source_document="doc1", source_section="auto")
        
        verdict, category, reasoning_trace_str, confidence = self.reasoning_agent.evaluate(dummy_claim, chains)
        
        reasoning_trace = reasoning_trace_str.split("\n")

        # ── Trust Score ───────────────────────────────────────────────
        contradiction_found = (verdict == VerificationVerdict.CONTRADICTION)
        
        trust_score = self.scorer.calculate_claim_score(
            verdict=verdict,
            evidence_count=len(chains),
            evidence_quality=0.9 if chains else 0.1,
            evidence_diversity=0.8 if len(chains) > 1 else 0.4,
            verification_confidence=confidence / 100.0,
            contradiction_found=contradiction_found
        )
        reasoning_trace.append(f"Verdict: {verdict.value}")
        reasoning_trace.append(f"Trust score: {trust_score}")

        return VerificationResult(
            claim_id=normalized_claim.claim_id,
            verdict=verdict,
            trust_score=trust_score,
            supporting_evidence=[],
            reasoning_trace=reasoning_trace,
            verification_timestamp=datetime.now(timezone.utc),
            verification_version="2.0.0"
        )
