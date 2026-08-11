from abc import ABC, abstractmethod
from typing import List
from app.models.knowledge.repository_knowledge_graph import RepositoryKnowledgeGraph
from app.models.knowledge.evidence import EvidenceItem


class EvidenceProvider(ABC):
    """
    Base contract for all evidence extraction strategies.
    Each provider specializes in finding a specific type of evidence
    from the Knowledge Graph (e.g., Dependencies, Imports, Annotations).
    """

    @abstractmethod
    def extract_evidence(
            self, graph: RepositoryKnowledgeGraph) -> List[EvidenceItem]:
        """
        Extract evidence items from the graph.
        """
