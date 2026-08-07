"""
Graph Analytics Engine

Implements graph-theoretic algorithms over the Neo4j Knowledge Graph.
Provides Centrality, Shortest Path, Reachability, Dependency Analysis,
and Cycle Detection as first-class research contributions.

Architecture position: Knowledge Graph → Graph Analytics → Evidence Retrieval
"""
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, field


@dataclass
class NodeCentrality:
    node_id: str
    node_label: str
    name: str
    degree: int = 0
    in_degree: int = 0
    out_degree: int = 0
    betweenness_score: float = 0.0
    structural_importance: str = "LOW"   # LOW | MEDIUM | HIGH | CRITICAL


@dataclass
class PathResult:
    source: str
    target: str
    path_nodes: List[str] = field(default_factory=list)
    path_relationships: List[str] = field(default_factory=list)
    path_length: int = 0
    reachable: bool = False


@dataclass
class DependencyNode:
    name: str
    qualified_name: str
    dependents: List[str] = field(default_factory=list)    # who depends on this
    dependencies: List[str] = field(default_factory=list)  # what this depends on
    dependency_depth: int = 0
    is_leaf: bool = False
    is_root: bool = False


@dataclass
class CycleReport:
    has_cycles: bool = False
    cycle_paths: List[List[str]] = field(default_factory=list)
    total_cycle_count: int = 0


@dataclass
class GraphAnalyticsReport:
    """Aggregated output of all graph analytics algorithms."""
    centrality_nodes: List[NodeCentrality] = field(default_factory=list)
    critical_nodes: List[NodeCentrality] = field(default_factory=list)
    dependency_graph: List[DependencyNode] = field(default_factory=list)
    cycle_report: CycleReport = field(default_factory=CycleReport)
    total_nodes: int = 0
    total_relationships: int = 0
    graph_density: float = 0.0


class GraphAnalyticsEngine:
    """
    Executes graph-theoretic algorithms over the Neo4j Knowledge Graph.
    Provides structural insights that strengthen evidence reasoning.
    """

    def __init__(self, repo=None):
        self.repo = repo

    def run_full_analytics(self) -> GraphAnalyticsReport:
        """Run the complete analytics pipeline and return a unified report."""
        report = GraphAnalyticsReport()

        report.total_nodes = self._count_nodes()
        report.total_relationships = self._count_relationships()
        if report.total_nodes > 0:
            report.graph_density = round(
                report.total_relationships / (report.total_nodes * (report.total_nodes - 1) + 1), 4
            )

        report.centrality_nodes = self.compute_degree_centrality()
        report.critical_nodes = [n for n in report.centrality_nodes
                                  if n.structural_importance in ("HIGH", "CRITICAL")]
        report.dependency_graph = self.analyze_dependencies()
        report.cycle_report = self.detect_cycles()

        return report

    # ─── 1. Degree Centrality ─────────────────────────────────────────────────

    def compute_degree_centrality(self) -> List[NodeCentrality]:
        """
        Computes degree centrality for every Class and Interface node.
        Degree = total number of incoming + outgoing relationships.
        High-degree nodes are architectural hotspots.
        """
        query = """
        MATCH (n)
        WHERE n:Class OR n:Interface OR n:Method
        OPTIONAL MATCH (n)-[out]->(m)
        OPTIONAL MATCH (p)-[in]->(n)
        WITH n, count(DISTINCT out) as out_deg, count(DISTINCT in) as in_deg
        RETURN labels(n)[0] as label, n.name as name, id(n) as node_id,
               out_deg, in_deg, (out_deg + in_deg) as total_degree
        ORDER BY total_degree DESC LIMIT 50
        """
        results = self._query(query, {})
        nodes = []
        for r in results:
            total = r.get("total_degree", 0)
            importance = "LOW"
            if total >= 20:
                importance = "CRITICAL"
            elif total >= 10:
                importance = "HIGH"
            elif total >= 5:
                importance = "MEDIUM"

            nodes.append(NodeCentrality(
                node_id=str(r.get("node_id", "")),
                node_label=r.get("label", "Unknown"),
                name=r.get("name", "Unknown"),
                degree=total,
                in_degree=r.get("in_deg", 0),
                out_degree=r.get("out_deg", 0),
                structural_importance=importance
            ))
        return nodes

    # ─── 2. Betweenness / PageRank (simulated if GDS not available) ───────────

    def compute_betweenness_approximation(self) -> List[Tuple[str, float]]:
        """
        Approximates betweenness by counting nodes that sit at the junction
        of CALLS relationships — a proxy for broker nodes in the call graph.
        """
        query = """
        MATCH (caller:Method)-[:CALLS]->(callee:Method)
        WITH callee, count(DISTINCT caller) as callers
        RETURN callee.name as name, callers
        ORDER BY callers DESC LIMIT 20
        """
        results = self._query(query, {})
        return [(r.get("name", ""), r.get("callers", 0)) for r in results]

    # ─── 3. Shortest Path ─────────────────────────────────────────────────────

    def shortest_path(self, source_name: str, target_name: str) -> PathResult:
        """
        Finds the shortest path between two named nodes in the graph.
        Used to prove architectural reachability (e.g. Controller → Repository).
        """
        query = """
        MATCH (src), (tgt)
        WHERE src.name = $source AND tgt.name = $target
        MATCH path = shortestPath((src)-[*..10]-(tgt))
        RETURN [n IN nodes(path) | n.name] as path_nodes,
               [r IN relationships(path) | type(r)] as path_rels,
               length(path) as path_length
        LIMIT 1
        """
        results = self._query(query, {"source": source_name, "target": target_name})
        if results:
            r = results[0]
            return PathResult(
                source=source_name,
                target=target_name,
                path_nodes=r.get("path_nodes", []),
                path_relationships=r.get("path_rels", []),
                path_length=r.get("path_length", 0),
                reachable=True
            )
        return PathResult(source=source_name, target=target_name, reachable=False)

    # ─── 4. Reachability ─────────────────────────────────────────────────────

    def check_reachability(self, source_name: str, target_label: str) -> List[str]:
        """
        Returns all nodes of target_label reachable from source_name.
        Used to verify architectural completeness (e.g., Security reaches Repository).
        """
        query = """
        MATCH (src {name: $source})-[*1..5]->(target)
        WHERE $label IN labels(target)
        RETURN DISTINCT target.name as name
        LIMIT 30
        """
        results = self._query(query, {"source": source_name, "label": target_label})
        return [r.get("name", "") for r in results if r.get("name")]

    # ─── 5. Dependency Analysis ───────────────────────────────────────────────

    def analyze_dependencies(self) -> List[DependencyNode]:
        """
        Builds a dependency map of all IMPORTS and DEPENDS_ON relationships.
        Identifies leaf nodes (no dependencies) and root nodes (no dependents).
        """
        query = """
        MATCH (src:Class)
        OPTIONAL MATCH (src)-[:IMPORTS|DEPENDS_ON]->(dep)
        OPTIONAL MATCH (caller)-[:IMPORTS|DEPENDS_ON]->(src)
        WITH src, collect(DISTINCT dep.name) as deps, collect(DISTINCT caller.name) as callers
        RETURN src.name as name,
               coalesce(src.qualified_name, src.name) as qualified_name,
               deps, callers
        LIMIT 100
        """
        results = self._query(query, {})
        nodes = []
        for r in results:
            deps = [d for d in r.get("deps", []) if d]
            callers = [c for c in r.get("callers", []) if c]
            nodes.append(DependencyNode(
                name=r.get("name", "Unknown"),
                qualified_name=r.get("qualified_name", r.get("name", "Unknown")),
                dependencies=deps,
                dependents=callers,
                dependency_depth=len(deps),
                is_leaf=(len(deps) == 0),
                is_root=(len(callers) == 0)
            ))
        return nodes

    # ─── 6. Cycle Detection ───────────────────────────────────────────────────

    def detect_cycles(self) -> CycleReport:
        """
        Detects circular dependencies in the IMPORTS / CALLS relationships.
        Circular dependencies are architectural anti-patterns that weaken trust.
        """
        query = """
        MATCH path = (a:Class)-[:IMPORTS|CALLS*2..5]->(a)
        RETURN [n IN nodes(path) | n.name] as cycle
        LIMIT 10
        """
        results = self._query(query, {})
        cycles = [r.get("cycle", []) for r in results if r.get("cycle")]
        return CycleReport(
            has_cycles=len(cycles) > 0,
            cycle_paths=cycles,
            total_cycle_count=len(cycles)
        )

    # ─── Internal helpers ─────────────────────────────────────────────────────

    def _query(self, cypher: str, params: dict) -> list:
        if not self.repo:
            return []
        try:
            return self.repo.conn.query(cypher, params) or []
        except Exception:
            return []

    def _count_nodes(self) -> int:
        results = self._query("MATCH (n) RETURN count(n) as cnt", {})
        return results[0].get("cnt", 0) if results else 0

    def _count_relationships(self) -> int:
        results = self._query("MATCH ()-[r]->() RETURN count(r) as cnt", {})
        return results[0].get("cnt", 0) if results else 0
