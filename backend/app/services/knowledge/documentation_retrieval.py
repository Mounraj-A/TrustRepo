from app.models.claim import Claim
from app.models.knowledge.evidence import EvidenceCandidate
from typing import List


class DocumentationRetrievalEngine:
    """Searches Markdown docs (README, CONTRIBUTING, etc)."""

    def __init__(self):
        pass

    def retrieve(self, claim: Claim) -> List[EvidenceCandidate]:
        return []
