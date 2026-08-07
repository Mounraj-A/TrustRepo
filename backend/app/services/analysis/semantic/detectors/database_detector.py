"""
DatabaseDetector — Semantic Feature Detector Plugin

Queries the RepositoryKnowledgeGraph for Annotation, Import, and
Dependency nodes that indicate database/ORM usage.
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

ORM_ANNOTATIONS = {
    "Entity", "Table", "Column", "Id", "GeneratedValue",
    "ManyToOne", "OneToMany", "ManyToMany", "OneToOne",
    "JoinColumn", "MappedSuperclass", "Embeddable",
}
ORM_IMPORTS = {
    "javax.persistence", "jakarta.persistence",
    "org.hibernate", "org.springframework.data.jpa",
    "sqlalchemy", "django.db.models", "peewee",
    "typeorm", "sequelize", "mongoose",
}
GRAPH_DB_IMPORTS = {
    "neo4j", "py2neo", "neomodel",
    "org.springframework.data.neo4j",
}
CACHE_IMPORTS = {
    "redis", "aioredis", "memcache", "pylibmc",
    "spring.data.redis", "jedis",
}


class DatabaseDetector(BaseFeatureDetector):
    """
    Detects database features (ORM, Graph DB, Caching) from the Knowledge Graph.
    """

    def detect(self, graph: RepositoryKnowledgeGraph) -> List[FeatureInstance]:
        features = []

        # ── ORM ───────────────────────────────────────────────────────────────
        orm_ann_nodes = self._get_annotation_nodes_matching(graph, ORM_ANNOTATIONS)
        orm_imp_nodes = self._get_import_nodes_matching(graph, ORM_IMPORTS)
        orm_dep_nodes = self._get_dependency_nodes_matching(graph, ORM_IMPORTS)
        orm_nodes = orm_ann_nodes[:3] + orm_imp_nodes[:3] + orm_dep_nodes[:2]
        if orm_nodes:
            chain = self._build_chain(orm_nodes, "ORM / Database Persistence", "ORM detected via annotations and imports.")
            self._append_feature(features, "feat_orm", [chain])

        # ── Graph Database ────────────────────────────────────────────────────
        graph_db_nodes = (
            self._get_import_nodes_matching(graph, GRAPH_DB_IMPORTS) +
            self._get_dependency_nodes_matching(graph, GRAPH_DB_IMPORTS)
        )
        if graph_db_nodes:
            chain = self._build_chain(graph_db_nodes[:5], "Graph Database", "Graph database imports/dependencies detected.")
            self._append_feature(features, "feat_graph_database", [chain])

        # ── Caching ───────────────────────────────────────────────────────────
        cache_nodes = (
            self._get_import_nodes_matching(graph, CACHE_IMPORTS) +
            self._get_dependency_nodes_matching(graph, CACHE_IMPORTS)
        )
        if cache_nodes:
            chain = self._build_chain(cache_nodes[:5], "Caching", "Caching library imports/dependencies detected.")
            self._append_feature(features, "feat_caching", [chain])

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

    def _build_chain(self, nodes: list, context_type: str, reasoning: str) -> EvidenceChain:
        items = [
            EvidenceItem(
                source=EvidenceSource(file_path=n.properties.get("file_path", "unknown")),
                node_type=n.label,
                symbol=n.properties.get("name", ""),
                context_type=context_type,
                graph_node_id=str(id(n)),
                evidence_strength=EvidenceStrength.PRIMARY,
            )
            for n in nodes
        ]
        return EvidenceChain(
            chain_id=f"chain_{uuid.uuid4().hex[:8]}",
            chain_type=context_type,
            sequence=items,
            reasoning_trace=reasoning,
        )
