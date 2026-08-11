from app.models.claim import Claim
from app.models.knowledge.evidence import EvidenceCandidate
from typing import List


class SemanticRetrievalEngine:
    """
    In-memory semantic embedding search (stub for FAISS).
    """

    def __init__(self):
        self.documents = []

    def add_documents(self, docs: List[str]):
        self.documents.extend(docs)

    def retrieve(self, claim: Claim) -> List[EvidenceCandidate]:
        # Return a mock semantic match for now
        return [
            EvidenceCandidate(
                source_engine="semantic",
                content=f"Semantically matched chunk related to: {claim.text}",
                metadata={"score": 0.85, "mocked": True}
            )
        ]
