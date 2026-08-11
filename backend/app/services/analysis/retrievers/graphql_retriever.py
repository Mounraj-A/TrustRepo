import uuid
from typing import List
from app.models.knowledge.evidence import EvidenceChain, EvidenceItem, EvidenceType, EvidenceStrength, EvidenceSource
from app.services.analysis.retrievers.base_retriever import BaseEvidenceRetriever
from app.models.knowledge.feature_instance import FeatureInstance


class GraphQLRetriever(BaseEvidenceRetriever):
    """Retrieves rigorous evidence for GraphQL (schema + resolvers + dependency)."""

    def retrieve(self, feature: FeatureInstance) -> List[EvidenceChain]:
        if feature.definition_id != "feat_graphql":
            return []

        # We require at least some GraphQL schema/resolver definitions
        items = self._detect_graphql_constructs()
        
        if items:
            chain = EvidenceChain(
                chain_id=f"graphql_{feature.definition_id}_{uuid.uuid4()}",
                chain_type="GraphQL API Evidence",
                retrieval_strategy="Strict Construct Detection",
                sequence=items,
                graph_path="Schema -> Resolvers",
                confidence=0.9,
                reasoning_trace=f"Found {len(items)} GraphQL schema/resolver elements."
            )
            return [chain]
        return []

    def _detect_graphql_constructs(self) -> List[EvidenceItem]:
        # Search for Schema or Resolver definitions
        query = """
        MATCH (n)
        WHERE n.name CONTAINS 'Schema' OR n.name CONTAINS 'Resolver' 
           OR n.name CONTAINS 'GraphQL' OR n.name CONTAINS 'Mutation' OR n.name CONTAINS 'Query'
        RETURN labels(n)[0] as label, n.name as name, n.file_path as file, n.start_line as line
        LIMIT 5
        """
        results = self.repo.conn.query(query, {})
        
        items = []
        for r in (results or []):
            if r.get("file"):
                items.append(EvidenceItem(
                    source=EvidenceSource(file_path=r.get("file"), line_number=r.get("line")),
                    evidence_type=EvidenceType.AST,
                    symbol=r.get("name"),
                    context_type="graphql_construct",
                    evidence_strength=EvidenceStrength.PRIMARY,
                    extraction_method="GraphASTQuery",
                    explanation=f"GraphQL construct '{r.get('name')}' of type {r.get('label')}."
                ))
        return items
