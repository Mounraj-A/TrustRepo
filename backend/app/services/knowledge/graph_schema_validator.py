"""
Graph Schema Validator — Phase 7

Validates the in-memory RepositoryKnowledgeGraph after it is built by GraphBuilder.
Ensures every node has required properties, detects duplicates, and computes
graph integrity metrics.

Output
------
GraphValidationReport:
    is_valid         : bool
    node_count       : int
    edge_count       : int
    missing_props    : List[str]   — nodes missing required properties
    duplicate_nodes  : int
    isolated_nodes   : int
    density_score    : float       — edges / (nodes * (nodes - 1))
    integrity_score  : float       — 1.0 minus penalty for each violation
    warnings         : List[str]
    errors           : List[str]
"""
from dataclasses import dataclass, field
from typing import List, Dict, Set
from app.models.knowledge.repository_knowledge_graph import RepositoryKnowledgeGraph


# Required properties per node label
REQUIRED_PROPERTIES: Dict[str, List[str]] = {
    "File":         ["path"],
    "Class":        ["name", "file_path"],
    "Method":       ["name", "file_path"],
    "Function":     ["name", "file_path"],
    "Import":       ["name"],
    "Dependency":   ["name"],
    "Annotation":   ["name"],
    "Package":      ["name"],
    "Interface":    ["name", "file_path"],
    "Inherits":     ["name"],
    "Call":         ["name"],
    "TypeAnnotation": ["name"],
}


@dataclass
class GraphValidationReport:
    is_valid: bool = True
    node_count: int = 0
    edge_count: int = 0
    missing_props: List[str] = field(default_factory=list)
    duplicate_nodes: int = 0
    isolated_nodes: int = 0
    density_score: float = 0.0
    integrity_score: float = 1.0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "is_valid": self.is_valid,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "missing_required_properties": len(self.missing_props),
            "duplicate_nodes": self.duplicate_nodes,
            "isolated_nodes": self.isolated_nodes,
            "density_score": round(self.density_score, 4),
            "integrity_score": round(self.integrity_score, 4),
            "warnings": self.warnings,
            "errors": self.errors,
        }


class GraphSchemaValidator:
    """
    Validates a RepositoryKnowledgeGraph against the node schema contract.

    Called after GraphBuilder.build() and before any discovery engines run.
    Violations are reported but do not stop the pipeline — warnings vs errors
    are distinguished so the caller can decide on severity.
    """

    def validate(self, graph: RepositoryKnowledgeGraph) -> GraphValidationReport:
        report = GraphValidationReport()

        if not graph or not graph.nodes:
            report.errors.append("Graph is empty — no nodes were built.")
            report.is_valid = False
            return report

        report.node_count = len(graph.nodes)
        report.edge_count = len(graph.edges)

        # ── 1. Required Property Validation ──────────────────────────────────
        missing_count = 0
        for node in graph.nodes:
            required = REQUIRED_PROPERTIES.get(node.label, [])
            for prop in required:
                val = node.properties.get(prop)
                if not val:
                    report.missing_props.append(
                        f"{node.label}[id={getattr(node, 'id', '?')}] missing '{prop}'"
                    )
                    missing_count += 1

        if missing_count > 0:
            report.warnings.append(
                f"{missing_count} node properties missing required values. "
                "Graph may produce incomplete evidence."
            )

        # ── 2. Duplicate Detection ────────────────────────────────────────────
        seen: Set[str] = set()
        dup_count = 0
        for node in graph.nodes:
            key = f"{node.label}:{node.properties.get('name', '')}:{node.properties.get('file_path', '')}"
            if key in seen:
                dup_count += 1
            seen.add(key)

        report.duplicate_nodes = dup_count
        if dup_count > 0:
            report.warnings.append(
                f"{dup_count} duplicate nodes detected. "
                "Technology detection may double-count evidence."
            )

        # ── 3. Isolated Node Detection ────────────────────────────────────────
        connected_ids: Set = set()
        for edge in graph.edges:
            connected_ids.add(id(edge.source) if hasattr(edge, 'source') else None)
            connected_ids.add(id(edge.target) if hasattr(edge, 'target') else None)

        isolated = [n for n in graph.nodes if id(n) not in connected_ids]
        report.isolated_nodes = len(isolated)
        if report.isolated_nodes > report.node_count * 0.5:
            report.warnings.append(
                f"Graph has {report.isolated_nodes}/{report.node_count} isolated nodes "
                f"({100 * report.isolated_nodes // report.node_count}%). "
                "Relationship extraction may be incomplete."
            )

        # ── 4. Density Score ─────────────────────────────────────────────────
        n = report.node_count
        if n > 1:
            max_edges = n * (n - 1)
            report.density_score = report.edge_count / max_edges
        else:
            report.density_score = 0.0

        # ── 5. Integrity Score ────────────────────────────────────────────────
        penalty = 0.0
        if missing_count > 0:
            penalty += min(0.3, missing_count / max(1, report.node_count) * 2)
        if dup_count > 0:
            penalty += min(0.2, dup_count / max(1, report.node_count))
        report.integrity_score = max(0.0, 1.0 - penalty)

        # ── 6. Final Validity ─────────────────────────────────────────────────
        if report.errors:
            report.is_valid = False
        elif report.integrity_score < 0.5:
            report.is_valid = False
            report.errors.append(
                f"Integrity score {report.integrity_score:.2f} below threshold 0.5. "
                "Graph quality is too low for reliable evidence detection."
            )

        return report
