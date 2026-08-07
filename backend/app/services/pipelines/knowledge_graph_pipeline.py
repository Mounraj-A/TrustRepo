"""
KnowledgeGraphPipeline — Layer 3

Wires:
1. GraphBuilder          → RepositoryKnowledgeGraph (in-memory model)
2. GraphRepository       → Neo4j persistence (nodes + edges)
3. Graph algorithm suite → Call/Dependency/Inheritance/Package/Module graphs
4. TechnologyDetection   → EvidenceChain-backed tech detection
5. ArchitectureDetection → Architecture pattern detection
6. GraphAnalyticsEngine  → Centrality, Shortest Path, Reachability,
                           Dependency Analysis, Cycle Detection
"""
from app.models.trustrepo_context import TrustRepoContext
from app.services.knowledge.graph_builder import GraphBuilder
from app.services.knowledge.graph_schema_validator import GraphSchemaValidator
from app.repositories.graph_repository import GraphRepository
from app.services.analysis.graph_algorithms.call_graph_builder import CallGraphBuilder
from app.services.analysis.graph_algorithms.dependency_graph_builder import DependencyGraphBuilder
from app.services.analysis.graph_algorithms.inheritance_graph_builder import InheritanceGraphBuilder
from app.services.analysis.graph_algorithms.package_graph_builder import PackageGraphBuilder
from app.services.analysis.graph_algorithms.module_graph_builder import ModuleGraphBuilder
from app.services.analysis.technology_detection import TechnologyDetection
from app.services.analysis.architecture_detection import ArchitectureDetection
from app.services.knowledge.graph_analytics_engine import GraphAnalyticsEngine

from app.services.analysis.semantic.feature_extractor import FeatureExtractor
from app.services.analysis.semantic.capability_detector import CapabilityDetector
from app.services.analysis.semantic.graph_enrichment_engine import GraphEnrichmentEngine


class KnowledgeGraphPipeline:
    def __init__(self):
        self.builder = GraphBuilder()
        self.schema_validator = GraphSchemaValidator()
        self.repo = GraphRepository()
        self.graph_algorithms = [
            CallGraphBuilder(),
            DependencyGraphBuilder(),
            InheritanceGraphBuilder(),
            PackageGraphBuilder(),
            ModuleGraphBuilder(),
        ]
        self.tech_detection = TechnologyDetection(repo=self.repo)
        self.arch_detection = ArchitectureDetection()
        self.analytics_engine = GraphAnalyticsEngine(repo=self.repo)

        self.feature_extractor = FeatureExtractor()
        self.capability_detector = CapabilityDetector()
        self.enrichment_engine = GraphEnrichmentEngine(repo=self.repo)

    def run(self, context: TrustRepoContext) -> TrustRepoContext:
        if not context.code_context:
            print("  [KGPipeline] No code context — skipping graph build.")
            return context

        # ── Step 1: Build In-Memory Graph Model ───────────────────────────────
        graph = self.builder.build(context.code_context)
        context.graph_context.graph = graph
        print(f"  Graph Built: {len(graph.nodes)} nodes, {len(graph.edges)} edges.")

        # ── Step 1b: Schema Validation ─────────────────────────────────────────
        validation = self.schema_validator.validate(graph)
        context.graph_context.analytics["schema_validation"] = validation.to_dict()
        if validation.errors:
            for err in validation.errors:
                print(f"  [GraphSchema] ERROR: {err}")
        for warn in validation.warnings:
            print(f"  [GraphSchema] WARN: {warn}")
        print(f"  Graph Integrity: {validation.integrity_score:.2f} | Nodes: {validation.node_count} | Edges: {validation.edge_count}")

        # ── Step 2: Persist to Neo4j ──────────────────────────────────────────
        try:
            self.repo.clear_graph()
            self.repo.save_graph(graph)
            print("  Graph persisted to Neo4j.")
        except Exception as e:
            print(f"  [KGPipeline] Neo4j persistence failed: {e}")

        # ── Step 3: Run Graph Algorithm Suite ─────────────────────────────────
        for algo in self.graph_algorithms:
            try:
                if hasattr(algo, 'build'):
                    algo.build()
            except Exception as e:
                print(f"  [KGPipeline] Algorithm {algo.__class__.__name__} failed: {e}")
        print("  Graph algorithms completed.")

        # ── Step 4: Technology Detection (EvidenceChain-backed) ───────────────
        try:
            tech_results = self.tech_detection.detect(graph)
            context.semantic_context.technologies = tech_results.get("technologies", [])
            context.semantic_context.technology_categories = tech_results.get("technology_categories", {})
            context.semantic_context.capabilities.extend(tech_results.get("capabilities", []))
            context.semantic_context.evidence_chains.extend(tech_results.get("evidence_chains", []))
        except Exception as e:
            print(f"  [KGPipeline] Technology detection failed: {e}")

        # ── Step 5: Feature Extraction (Plugin Detectors + Fusion + Validation)
        # CRITICAL: Pass the in-memory RepositoryKnowledgeGraph — NOT RepositoryContext.
        # All feature detector plugins query graph nodes directly (same as TechnologyDetection).
        # Previously they attempted live Neo4j Cypher queries (always None) — now fixed.
        try:
            features = self.feature_extractor.extract(graph)
            context.semantic_context.features = [f.canonical_name for f in features]
        except Exception as e:
            print(f"  [KGPipeline] Feature extraction failed: {e}")
            features = []

        # ── Step 6: Capability Detection ─────────────────────────────────────
        try:
            detected_caps = self.capability_detector.detect(features)
            context.semantic_context.capabilities.extend(detected_caps)
            # Deduplicate
            context.semantic_context.capabilities = sorted(list(set(context.semantic_context.capabilities)))
        except Exception as e:
            print(f"  [KGPipeline] Capability detection failed: {e}")
            
        # ── Step 7: Architecture Detection
        try:
            detected_arch = self.arch_detection.detect(features)
            context.semantic_context.architectures = detected_arch
        except Exception as e:
            print(f"  [KGPipeline] Architecture detection failed: {e}")
            
        # ── Step 8: Graph Enrichment
        try:
            self.enrichment_engine.enrich(features)
        except Exception as e:
            print(f"  [KGPipeline] Graph enrichment failed: {e}")

        # ── Step 9: Graph Analytics Engine ────────────────────────────────────
        try:
            analytics_report = self.analytics_engine.run_full_analytics()
            context.graph_context.analytics = {
                "total_nodes":        analytics_report.total_nodes,
                "total_relationships": analytics_report.total_relationships,
                "graph_density":      analytics_report.graph_density,
                "critical_nodes":     [
                    {"name": n.name, "degree": n.degree, "importance": n.structural_importance}
                    for n in analytics_report.critical_nodes
                ],
                "cycle_detected":     analytics_report.cycle_report.has_cycles,
                "cycle_count":        analytics_report.cycle_report.total_cycle_count,
            }
            print(
                f"  Analytics: {analytics_report.total_nodes} nodes, "
                f"{len(analytics_report.critical_nodes)} critical, "
                f"cycles={'YES' if analytics_report.cycle_report.has_cycles else 'NO'}"
            )
        except Exception as e:
            print(f"  [KGPipeline] Graph analytics failed: {e}")

        return context
