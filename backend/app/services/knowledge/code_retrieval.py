from app.models.claim import Claim
from app.models.knowledge.evidence import EvidenceCandidate
from typing import List


class CodeRetrievalEngine:
    """Searches raw source files or UIR for exact symbols."""

    def __init__(self):
        pass

    def retrieve(self, claim: Claim) -> List[EvidenceCandidate]:
        return []
