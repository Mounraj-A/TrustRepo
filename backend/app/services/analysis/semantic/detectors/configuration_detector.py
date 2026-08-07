"""
ConfigurationDetector — Semantic Feature Detector Plugin

Detects infrastructure and configuration features from the Knowledge Graph.
Looks for Dependency nodes created by the DependencyParser from Dockerfile,
docker-compose.yml, and other infrastructure files.

Also queries the graph for configuration-related File nodes.
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

DOCKER_KEYWORDS = {"dockerfile", "docker-compose", "compose.yaml", "compose.yml"}
CELERY_IMPORTS = {"celery", "kombu"}
MESSAGE_QUEUE_IMPORTS = {
    "pika", "aio_pika", "aioamqp",
    "confluent_kafka", "kafka", "kafka-python",
    "org.springframework.amqp", "org.springframework.kafka",
}
CONTAINERIZATION_IMPORTS = {"docker", "podman"}


class ConfigurationDetector(BaseFeatureDetector):
    """
    Detects containerization, async tasks, and message queue features
    by querying File and Dependency nodes in the Knowledge Graph.
    """

    def detect(self, graph: RepositoryKnowledgeGraph) -> List[FeatureInstance]:
        features = []

        # ── Containerization (Docker) ─────────────────────────────────────────
        docker_nodes = self._find_docker_nodes(graph)
        if docker_nodes:
            chain = self._build_chain(
                docker_nodes, "Containerization",
                "Docker or docker-compose configuration files found in the Knowledge Graph.",
            )
            self._append_feature(features, "feat_docker", [chain])

        # ── Task Queue (Celery) ───────────────────────────────────────────────
        celery_nodes = self._get_import_nodes_matching(graph, CELERY_IMPORTS)
        if celery_nodes:
            chain = self._build_chain(
                celery_nodes[:5], "Async Task Queue",
                "Celery distributed task queue imports detected.",
            )
            self._append_feature(features, "feat_task_queue", [chain])

        # ── Message Queue ─────────────────────────────────────────────────────
        mq_nodes = (
            self._get_import_nodes_matching(graph, MESSAGE_QUEUE_IMPORTS) +
            self._get_dependency_nodes_matching(graph, MESSAGE_QUEUE_IMPORTS)
        )
        if mq_nodes:
            chain = self._build_chain(
                mq_nodes[:5], "Message Queue",
                "Message queue library imports/dependencies detected.",
            )
            self._append_feature(features, "feat_event_streaming", [chain])

        return features

    def _find_docker_nodes(self, graph: RepositoryKnowledgeGraph) -> list:
        """Find File nodes that represent Docker infrastructure files."""
        result = []
        for node in graph.nodes:
            if node.label != "File":
                continue
            path = (node.properties.get("path", "") or node.properties.get("name", "")).lower()
            if any(kw in path for kw in DOCKER_KEYWORDS):
                result.append(node)
        return result[:5]

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
                source=EvidenceSource(file_path=n.properties.get("file_path", n.properties.get("path", "unknown"))),
                node_type=n.label,
                symbol=n.properties.get("name", n.properties.get("path", "")),
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
