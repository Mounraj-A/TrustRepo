from app.models.claim import Claim
from app.models.knowledge.investigation import InvestigationResult
from app.services.agents.base_agent import BaseAgent
from app.services.agents.repository_memory import RepositoryMemory
from app.services.analysis.evidence_collector import EvidenceCollector


class InvestigatorAgent(BaseAgent):
    """
    Actively researches a claim. Evaluates if we have enough evidence.
    Formulates new queries if not, but does NOT perform the final verification.
    """

    def __init__(self):
        super().__init__()
        self.memory = RepositoryMemory()
        self.collector = EvidenceCollector()

    def investigate(self, claim: Claim) -> InvestigationResult:
        key = claim.id

        # 1. Initial Collection
        initial_context = self.collector.collect(claim)
        self.memory.store(key, initial_context)

        # 2. Agent Reasoning (Stub)
        context = self.memory.retrieve(key)

        confidence = 0.85 if len(context.candidates) > 0 else 0.2
        missing = ["Database connection logs"] if confidence < 0.9 else []
        reasoning = [
            "Analyzed initial context.",
            f"Found {len(context.candidates)} evidence candidates.",
            "Confidence is high based on topological match." if confidence > 0.8 else "Insufficient context."
        ]
        action = "Proceed to Verification" if confidence >= 0.5 else "Request more evidence"

        return InvestigationResult(
            evidence_context=context,
            confidence=confidence,
            missing_evidence=missing,
            reasoning_trace=reasoning,
            recommended_action=action,
            retrieval_attempts=1
        )
