from app.models.knowledge.evidence import EvidenceContext
from typing import Dict


class RepositoryMemory:
    """Short-term memory for the Agent during a verification session."""

    def __init__(self):
        self.memory: Dict[str, EvidenceContext] = {}

    def store(self, key: str, context: EvidenceContext):
        if key in self.memory:
            self.memory[key].add_candidates(context.candidates)
        else:
            self.memory[key] = context

    def retrieve(self, key: str) -> EvidenceContext:
        return self.memory.get(key)
