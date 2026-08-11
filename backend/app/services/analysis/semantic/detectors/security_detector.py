"""
SecurityDetector — Semantic Feature Detector Plugin

Queries the RepositoryKnowledgeGraph for Annotation and Import nodes
that indicate authentication, authorization, or security features.
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

RBAC_ANNOTATIONS = {
    "PreAuthorize", "Secured", "RolesAllowed", "RequiresRoles",
    "hasRole", "hasAuthority", "EnableWebSecurity", "EnableMethodSecurity",
    "login_required", "permission_required",
}
JWT_IMPORTS = {
    "jwt", "pyjwt", "io.jsonwebtoken", "com.auth0.jwt",
    "spring-security-jwt", "jsonwebtoken",
}
CORS_ANNOTATIONS = {
    "CrossOrigin", "CorsOrigin",
}
CORS_IMPORTS = {
    "flask_cors", "django.middleware.csrf", "cors", "fastapi.middleware.cors",
}
OAUTH_IMPORTS = {
    "oauthlib", "requests_oauthlib", "spring-security-oauth2",
    "org.springframework.security.oauth2", "authlib",
}


class SecurityDetector(BaseFeatureDetector):
    """
    Detects security features (RBAC, JWT, CORS, OAuth2) from the Knowledge Graph.
    """

    def detect(self, graph: RepositoryKnowledgeGraph) -> List[FeatureInstance]:
        features = []

        # ── RBAC ─────────────────────────────────────────────────────────────
        rbac_chain = self._find_annotation_chain(
            graph, RBAC_ANNOTATIONS, "Authorization", "feat_rbac",
            "Role-based access control annotations detected.",
        )
        if rbac_chain:
            self._append_feature(features, "feat_rbac", [rbac_chain])

        # ── JWT ──────────────────────────────────────────────────────────────
        jwt_chain = self._find_import_chain(
            graph, JWT_IMPORTS, "JWT Authentication", "feat_jwt",
            "JWT authentication imports detected.",
        )
        if jwt_chain:
            self._append_feature(features, "feat_jwt", [jwt_chain])

        # ── CORS ─────────────────────────────────────────────────────────────
        cors_ann_chain = self._find_annotation_chain(
            graph, CORS_ANNOTATIONS, "CORS", "feat_cors",
            "CORS annotation detected.",
        )
        cors_imp_chain = self._find_import_chain(
            graph, CORS_IMPORTS, "CORS", "feat_cors",
            "CORS middleware imports detected.",
        )
        if cors_ann_chain or cors_imp_chain:
            chains = [c for c in [cors_ann_chain, cors_imp_chain] if c]
            self._append_feature(features, "feat_cors", chains)

        # ── OAuth2 ───────────────────────────────────────────────────────────
        oauth_chain = self._find_import_chain(
            graph, OAUTH_IMPORTS, "OAuth2", "feat_oauth2",
            "OAuth2 library imports detected.",
        )
        if oauth_chain:
            self._append_feature(features, "feat_oauth2", [oauth_chain])

        return features

    def _append_feature(self, features: list, feat_id: str, chains: list):
        feat_def = SEMANTIC_REGISTRY.get_by_id(feat_id)
        if feat_def:
            features.append(FeatureInstance(
                id=f"inst_{uuid.uuid4().hex[:8]}",
                definition_id=feat_def.id,
                canonical_name=feat_def.canonical_name,
                evidence=chains,
            ))

    def _find_annotation_chain(
        self,
        graph: RepositoryKnowledgeGraph,
        names: set,
        context_type: str,
        feat_id: str,
        reasoning: str,
    ) -> Optional[EvidenceChain]:
        nodes = self._get_annotation_nodes_matching(graph, names)
        if not nodes:
            return None
        items = [
            EvidenceItem(
                source=EvidenceSource(
                    file_path=n.properties.get(
                        "file_path", "unknown")),
                node_type="Annotation",
                symbol=n.properties.get("name", ""),
                context_type=context_type,
                graph_node_id=str(id(n)),
                evidence_strength=EvidenceStrength.PRIMARY,
            )
            for n in nodes[:5]
        ]
        return EvidenceChain(
            chain_id=f"chain_{uuid.uuid4().hex[:8]}",
            chain_type=f"{feat_id} Annotations",
            sequence=items,
            reasoning_trace=reasoning,
        )

    def _find_import_chain(
        self,
        graph: RepositoryKnowledgeGraph,
        prefixes: set,
        context_type: str,
        feat_id: str,
        reasoning: str,
    ) -> Optional[EvidenceChain]:
        nodes = self._get_import_nodes_matching(graph, prefixes)
        if not nodes:
            return None
        items = [
            EvidenceItem(
                source=EvidenceSource(
                    file_path=n.properties.get(
                        "file_path", "unknown")),
                node_type="Import",
                symbol=n.properties.get("name", ""),
                context_type=context_type,
                graph_node_id=str(id(n)),
                evidence_strength=EvidenceStrength.PRIMARY,
            )
            for n in nodes[:5]
        ]
        return EvidenceChain(
            chain_id=f"chain_{uuid.uuid4().hex[:8]}",
            chain_type=f"{feat_id} Imports",
            sequence=items,
            reasoning_trace=reasoning,
        )
