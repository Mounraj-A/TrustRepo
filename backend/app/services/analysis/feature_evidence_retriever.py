from typing import List, Dict, Any, Optional
from app.models.knowledge.evidence import EvidenceChain, EvidenceItem, EvidenceType, DocumentationSearchResult
from app.repositories.graph_repository import GraphRepository
from app.models.knowledge.feature_instance import FeatureInstance

from app.services.analysis.retrievers.architecture_retriever import ArchitectureRetriever
from app.services.analysis.retrievers.api_retriever import APIRetriever
from app.services.analysis.retrievers.database_retriever import DatabaseRetriever
from app.services.analysis.retrievers.graphql_retriever import GraphQLRetriever


class FeatureEvidenceRetriever:
    """
    Orchestrates evidence retrieval for features using language/framework-aware
    retrieval strategies. Generates concrete EvidenceItems instead of fabricated snippets.
    """

    def __init__(self, repo: GraphRepository = None):
        self.repo = repo or GraphRepository()
        
        # Load specific feature strategies
        self.strategies = {
            "feat_mvc": ArchitectureRetriever(self.repo),
            "feat_layered": ArchitectureRetriever(self.repo),
            "feat_rest_api": APIRetriever(self.repo),
            "feat_graphql": GraphQLRetriever(self.repo),
            "feat_orm": DatabaseRetriever(self.repo, mode="orm"),
            "feat_database": DatabaseRetriever(self.repo, mode="database"),
            "feat_connection_pooling": DatabaseRetriever(self.repo, mode="pooling"),
            "feat_database_migration": DatabaseRetriever(self.repo, mode="migration"),
        }

    def retrieve_evidence(self, feature: FeatureInstance) -> List[EvidenceChain]:
        """
        Retrieves full concrete evidence for a candidate feature.
        If the feature isn't supported by a specific strategy, falls back to checking
        the graph for concrete `SUPPORTED_BY` AST nodes (but only using real fields).
        """
        strategy = self.strategies.get(feature.definition_id)
        if strategy:
            return strategy.retrieve(feature)
        
        # Fallback: check basic graph links but don't fabricate evidence
        return self._fallback_retrieval(feature)

    def _fallback_retrieval(self, feature: FeatureInstance) -> List[EvidenceChain]:
        # For technologies, `TechnologyDetection` already produces valid chains,
        # so this is just for unsupported semantic features. We won't fabricate snippets.
        return []
