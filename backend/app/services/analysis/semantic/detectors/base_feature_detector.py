from abc import ABC, abstractmethod
from typing import List

from app.models.repository_context import RepositoryContext
from app.models.knowledge.feature_instance import FeatureInstance
from app.repositories.graph_repository import GraphRepository

class BaseFeatureDetector(ABC):
    """
    Base class for all semantic feature detectors.
    Detectors emit FeatureInstances populated with evidence.
    They do NOT calculate confidence or map capabilities.
    """
    
    def __init__(self, repo: GraphRepository = None):
        self.repo = repo or GraphRepository()
        
    @abstractmethod
    def detect(self, context: RepositoryContext) -> List[FeatureInstance]:
        """
        Scan the repository context (and optionally the Neo4j graph)
        and return a list of detected feature instances.
        """
        pass
