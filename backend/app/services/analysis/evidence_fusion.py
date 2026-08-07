from typing import List
from app.models.knowledge.evidence import EvidenceCandidate

class EvidenceFusion:
    """Deduplicates and synthesizes retrieved evidence."""
    def fuse(self, candidates: List[EvidenceCandidate]) -> List[EvidenceCandidate]:
        seen = set()
        fused = []
        for c in candidates:
            if c.content not in seen:
                seen.add(c.content)
                fused.append(c)
        return fused
