from typing import List
from app.models.knowledge.evidence import EvidenceChain
from app.repositories.graph_repository import GraphRepository
from app.models.knowledge.feature_instance import FeatureInstance


class BaseEvidenceRetriever:
    """Base class for feature-specific evidence retrievers."""

    def __init__(self, repo: GraphRepository):
        self.repo = repo

    def retrieve(self, feature: FeatureInstance) -> List[EvidenceChain]:
        raise NotImplementedError("Subclasses must implement retrieve()")
