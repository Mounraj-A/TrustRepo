import uuid
from typing import List
from app.models.knowledge.evidence import EvidenceChain, EvidenceItem, EvidenceType, EvidenceStrength, EvidenceSource
from app.services.analysis.retrievers.base_retriever import BaseEvidenceRetriever
from app.models.knowledge.feature_instance import FeatureInstance


class APIRetriever(BaseEvidenceRetriever):
    """Retrieves evidence for REST API endpoints using framework-aware queries."""

    def retrieve(self, feature: FeatureInstance) -> List[EvidenceChain]:
        evidence_chains = []

        if feature.definition_id == "feat_rest_api":
            items = self._detect_rest_routes()
            if items:
                chain = EvidenceChain(
                    chain_id=f"api_{feature.definition_id}_{uuid.uuid4()}",
                    chain_type="REST API Evidence",
                    retrieval_strategy="Framework Route Detection",
                    sequence=items,
                    graph_path="Routes -> Endpoints",
                    confidence=0.9,
                    reasoning_trace=f"Found {len(items)} REST API endpoints."
                )
                evidence_chains.append(chain)

        return evidence_chains

    def _detect_rest_routes(self) -> List[EvidenceItem]:
        """
        Looks for annotations/decorators indicating a route (e.g., @app.route, @GetMapping, router.get)
        """
        query = """
        MATCH (a:Annotation)-[:ANNOTATES]->(m:Method)
        WHERE a.name IN ['route', 'get', 'post', 'put', 'delete', 'patch', 
                         'GetMapping', 'PostMapping', 'RequestMapping', 'RestController']
        RETURN a.name as decorator, m.name as endpoint, m.file_path as file, m.start_line as line
        LIMIT 5
        """
        results = self.repo.conn.query(query, {})
        if not results:
            # Fallback for JS/TS express router calls
            query_js = """
            MATCH (c:Call)-[:CALLS]->(m:Method)
            WHERE m.name IN ['get', 'post', 'put', 'delete'] AND c.name CONTAINS 'router'
            RETURN m.name as decorator, c.name as endpoint, c.file_path as file, c.start_line as line
            LIMIT 5
            """
            results = self.repo.conn.query(query_js, {})
            
        items = []
        for r in (results or []):
            items.append(EvidenceItem(
                source=EvidenceSource(file_path=r.get("file"), line_number=r.get("line")),
                evidence_type=EvidenceType.AST,
                symbol=r.get("endpoint"),
                context_type="api_endpoint",
                evidence_strength=EvidenceStrength.PRIMARY,
                extraction_method="GraphASTQuery",
                explanation=f"API Endpoint defined with '{r.get('decorator')}'."
            ))

        return items
