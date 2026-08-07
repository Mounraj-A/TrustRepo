import uuid
from typing import List

from app.models.repository_context import RepositoryContext
from app.models.knowledge.feature_instance import FeatureInstance
from app.models.knowledge.evidence import EvidenceChain, EvidenceItem, EvidenceSource, EvidenceStrength
from app.services.analysis.semantic.detectors.base_feature_detector import BaseFeatureDetector
from app.services.knowledge.semantic_registry import SEMANTIC_REGISTRY

class ApiDetector(BaseFeatureDetector):
    def detect(self, context: RepositoryContext) -> List[FeatureInstance]:
        features = []
        
        # Look for REST API evidence
        rest_evidence = self._find_rest_evidence()
        if rest_evidence:
            feat_def = SEMANTIC_REGISTRY.get_by_id("feat_rest_api")
            if feat_def:
                features.append(FeatureInstance(
                    id=f"inst_{uuid.uuid4().hex[:8]}",
                    definition_id=feat_def.id,
                    canonical_name=feat_def.canonical_name,
                    evidence=[rest_evidence]
                ))
                
        # Look for GraphQL evidence
        graphql_evidence = self._find_graphql_evidence()
        if graphql_evidence:
            feat_def = SEMANTIC_REGISTRY.get_by_id("feat_graphql")
            if feat_def:
                features.append(FeatureInstance(
                    id=f"inst_{uuid.uuid4().hex[:8]}",
                    definition_id=feat_def.id,
                    canonical_name=feat_def.canonical_name,
                    evidence=[graphql_evidence]
                ))

        return features

    def _find_rest_evidence(self) -> EvidenceChain:
        query = """
        MATCH (a:Annotation)
        WHERE a.name IN ['RestController', 'GetMapping', 'PostMapping', 'RequestMapping', 'route', 'app.get', 'app.post']
        RETURN a.name as name, a.file_path as file_path, id(a) as node_id
        LIMIT 5
        """
        try:
            results = self.repo.conn.query(query, {})
            if results:
                items = []
                for r in results:
                    items.append(EvidenceItem(
                        source=EvidenceSource(file_path=r.get("file_path", "unknown")),
                        node_type="Annotation",
                        symbol=r.get("name"),
                        context_type="API Endpoint",
                        graph_node_id=str(r.get("node_id")),
                        evidence_strength=EvidenceStrength.PRIMARY
                    ))
                return EvidenceChain(
                    chain_id=f"chain_{uuid.uuid4().hex[:8]}",
                    chain_type="REST API Annotations",
                    sequence=items,
                    reasoning_trace="Found explicit REST API annotations/decorators indicating endpoint exposure."
                )
        except Exception:
            pass
            
        # Fallback to tech detection evidence if no annotations found directly
        # E.g., FastAPI, Flask, Express
        return None

    def _find_graphql_evidence(self) -> EvidenceChain:
        query = """
        MATCH (a:Annotation)
        WHERE a.name IN ['GraphQLApi', 'Query', 'Mutation']
        RETURN a.name as name, a.file_path as file_path, id(a) as node_id
        LIMIT 5
        """
        try:
            results = self.repo.conn.query(query, {})
            if results:
                items = []
                for r in results:
                    items.append(EvidenceItem(
                        source=EvidenceSource(file_path=r.get("file_path", "unknown")),
                        node_type="Annotation",
                        symbol=r.get("name"),
                        context_type="GraphQL Schema",
                        graph_node_id=str(r.get("node_id")),
                        evidence_strength=EvidenceStrength.PRIMARY
                    ))
                return EvidenceChain(
                    chain_id=f"chain_{uuid.uuid4().hex[:8]}",
                    chain_type="GraphQL Annotations",
                    sequence=items,
                    reasoning_trace="Found GraphQL specific schema annotations."
                )
        except Exception:
            pass
            
        return None
