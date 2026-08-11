"""
ApiDetector — Semantic Feature Detector Plugin

Queries the RepositoryKnowledgeGraph for Annotation and Import nodes
that indicate REST or GraphQL API exposure.

Evidence Sources
----------------
- Annotation nodes: @RestController, @GetMapping, @route, @app.get, etc.
- Import nodes:     fastapi, flask, express, django.http, etc.
"""
import uuid
from typing import List, Optional

from app.models.knowledge.repository_knowledge_graph import RepositoryKnowledgeGraph
from app.models.knowledge.feature_instance import FeatureInstance
from app.models.knowledge.evidence import (
    EvidenceChain, EvidenceItem, EvidenceSource, EvidenceStrength
)
from app.services.analysis.semantic.detectors.base_feature_detector import BaseFeatureDetector
from app.services.knowledge.semantic_registry import SEMANTIC_REGISTRY

# Annotation names that indicate REST API exposure
REST_ANNOTATIONS = {
    "RestController", "Controller", "RequestMapping",
    "GetMapping", "PostMapping", "PutMapping", "DeleteMapping", "PatchMapping",
    "route", "app.get", "app.post", "app.put", "app.delete",
    "router.get", "router.post", "router.put", "router.delete",
    "api_view", "APIView",
}

# Import prefixes that indicate REST API frameworks
REST_IMPORT_PREFIXES = {
    "fastapi", "flask", "django.http", "django.views",
    "express", "koa", "hapi",
    "javax.ws.rs", "jakarta.ws.rs",
    "org.springframework.web.bind.annotation",
}

# GraphQL indicators
GRAPHQL_ANNOTATIONS = {
    "GraphQLApi",
    "Query",
    "Mutation",
    "Subscription",
    "Schema"}
GRAPHQL_IMPORTS = {"graphene", "strawberry", "ariadne", "graphql", "apollo"}


class ApiDetector(BaseFeatureDetector):
    """
    Detects REST and GraphQL API features from the Knowledge Graph.
    Queries Annotation and Import nodes — no Neo4j queries.
    """

    def detect(self, graph: RepositoryKnowledgeGraph) -> List[FeatureInstance]:
        features = []

        # ── REST API ─────────────────────────────────────────────────────────
        rest_chain = self._find_rest_evidence(graph)
        if rest_chain:
            feat_def = SEMANTIC_REGISTRY.get_by_id("feat_rest_api")
            if feat_def:
                features.append(FeatureInstance(
                    id=f"inst_{uuid.uuid4().hex[:8]}",
                    definition_id=feat_def.id,
                    canonical_name=feat_def.canonical_name,
                    evidence=[rest_chain],
                ))

        # ── GraphQL API ──────────────────────────────────────────────────────
        graphql_chain = self._find_graphql_evidence(graph)
        if graphql_chain:
            feat_def = SEMANTIC_REGISTRY.get_by_id("feat_graphql")
            if feat_def:
                features.append(FeatureInstance(
                    id=f"inst_{uuid.uuid4().hex[:8]}",
                    definition_id=feat_def.id,
                    canonical_name=feat_def.canonical_name,
                    evidence=[graphql_chain],
                ))

        return features

    def _find_rest_evidence(
            self, graph: RepositoryKnowledgeGraph) -> Optional[EvidenceChain]:
        annotation_nodes = self._get_annotation_nodes_matching(
            graph, REST_ANNOTATIONS)
        import_nodes = self._get_import_nodes_matching(
            graph, REST_IMPORT_PREFIXES)
        matched_nodes = annotation_nodes[:5] + import_nodes[:5]

        if not matched_nodes:
            return None

        items = [
            EvidenceItem(
                source=EvidenceSource(
                    file_path=n.properties.get(
                        "file_path", "unknown")),
                node_type=n.label,
                symbol=n.properties.get("name", ""),
                context_type="REST API",
                graph_node_id=str(id(n)),
                evidence_strength=EvidenceStrength.PRIMARY,
            )
            for n in matched_nodes
        ]
        return EvidenceChain(
            chain_id=f"chain_{uuid.uuid4().hex[:8]}",
            chain_type="REST API Detection",
            sequence=items,
            reasoning_trace=f"Found {
                len(items)} REST API indicators (annotations/imports) in the Knowledge Graph.",
        )

    def _find_graphql_evidence(
            self, graph: RepositoryKnowledgeGraph) -> Optional[EvidenceChain]:
        annotation_nodes = self._get_annotation_nodes_matching(
            graph, GRAPHQL_ANNOTATIONS)
        import_nodes = self._get_import_nodes_matching(graph, GRAPHQL_IMPORTS)
        matched_nodes = annotation_nodes[:5] + import_nodes[:5]

        if not matched_nodes:
            return None

        items = [
            EvidenceItem(
                source=EvidenceSource(
                    file_path=n.properties.get(
                        "file_path", "unknown")),
                node_type=n.label,
                symbol=n.properties.get("name", ""),
                context_type="GraphQL",
                graph_node_id=str(id(n)),
                evidence_strength=EvidenceStrength.PRIMARY,
            )
            for n in matched_nodes
        ]
        return EvidenceChain(
            chain_id=f"chain_{uuid.uuid4().hex[:8]}",
            chain_type="GraphQL Detection",
            sequence=items,
            reasoning_trace=f"Found {
                len(items)} GraphQL indicators in the Knowledge Graph.",
        )
