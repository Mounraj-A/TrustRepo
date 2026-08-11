"""
Base class for all semantic feature detector plugins.

ARCHITECTURE CONTRACT
---------------------
Input:  RepositoryKnowledgeGraph  (in-memory graph, always available)
Output: List[FeatureInstance]     (each with an EvidenceChain)

Detectors MUST NOT:
  - Query Neo4j / GraphRepository directly
  - Read source files directly
  - Use regex on raw file content

Detectors MUST:
  - Query graph.nodes by node.label
  - Build EvidenceChains from matched nodes
  - Return empty list (not None) if no evidence found
"""
from abc import ABC, abstractmethod
from typing import List

from app.models.knowledge.repository_knowledge_graph import RepositoryKnowledgeGraph
from app.models.knowledge.feature_instance import FeatureInstance


class BaseFeatureDetector(ABC):
    """
    Base class for semantic feature detector plugins.

    Each detector queries the in-memory RepositoryKnowledgeGraph
    for specific node patterns and emits FeatureInstances backed
    by EvidenceChains.
    """

    @abstractmethod
    def detect(self, graph: RepositoryKnowledgeGraph) -> List[FeatureInstance]:
        """
        Scan the Knowledge Graph and return detected feature instances.

        Parameters
        ----------
        graph : RepositoryKnowledgeGraph
            The fully built in-memory graph from GraphBuilder.

        Returns
        -------
        List[FeatureInstance]
            Detected features with evidence. Never None — return [] if empty.
        """

    # ── Shared Graph Query Helpers ──────────────────────────────────────────

    def _get_nodes_by_label(
            self, graph: RepositoryKnowledgeGraph, label: str) -> list:
        """Return all nodes matching a specific label."""
        return [n for n in graph.nodes if n.label == label]

    def _get_nodes_by_labels(
            self, graph: RepositoryKnowledgeGraph, labels: set) -> list:
        """Return all nodes whose label is in the given set."""
        return [n for n in graph.nodes if n.label in labels]

    def _get_annotation_nodes_matching(
        self,
        graph: RepositoryKnowledgeGraph,
        names: set,
    ) -> list:
        """Return Annotation nodes whose name (case-insensitive) is in the given set."""
        lower_names = {n.lower() for n in names}
        result = []
        for node in graph.nodes:
            if node.label != "Annotation":
                continue
            node_name = (
                node.properties.get("name", "") or
                node.properties.get("qualname", "")
            ).lower()
            if node_name in lower_names:
                result.append(node)
        return result

    def _get_import_nodes_matching(
        self,
        graph: RepositoryKnowledgeGraph,
        prefixes: set,
    ) -> list:
        """Return Import nodes whose name starts with any of the given prefixes."""
        result = []
        for node in graph.nodes:
            if node.label != "Import":
                continue
            name = (
                node.properties.get("name", "") or
                node.properties.get("qualname", "")
            ).lower()
            if any(name.startswith(p.lower()) for p in prefixes):
                result.append(node)
        return result

    def _get_dependency_nodes_matching(
        self,
        graph: RepositoryKnowledgeGraph,
        prefixes: set,
    ) -> list:
        """Return Dependency nodes whose name starts with any of the given prefixes."""
        result = []
        for node in graph.nodes:
            if node.label != "Dependency":
                continue
            name = (node.properties.get("name", "") or "").lower()
            if any(name.startswith(p.lower()) for p in prefixes):
                result.append(node)
        return result
