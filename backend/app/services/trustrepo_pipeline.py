"""
Master Orchestrator for the entire TrustRepo system.

Full pipeline execution order:
    Repository URL
        ↓  [Layer 1] RepositoryIngestionPipeline
    RepositoryContext
        ↓  [Layer 2A] DocumentUnderstandingPipeline (or Code Intelligence Mode if no docs)
    DocumentContext → Claims
        ↓  [Layer 2B] CodeUnderstandingPipeline
    CodeContext → AST → Semantic Passes → UIR → Symbols → Relationships
        ↓  [Layer 3] KnowledgeGraphPipeline
    RepositoryKnowledgeGraph → Schema Validation → TechDetection → FeatureExtraction
                             → CapabilityDetection → ArchDetection → GraphAnalytics
        ↓  [Layer 4] EvidencePipeline
    EvidenceContext per Claim (from KG + Semantic + Code + Docs)
        ↓  [Layer 5] InvestigationPipeline
    EvidenceFusion → EvidenceValidation → ReasoningAgent → VerificationResult per Claim
        ↓  [Layer 6] VerificationPipeline
    Verification Summary
        ↓  [Layer 7] ReportingPipeline
    RepositoryTrustReport
"""
import time
import os
import psutil
from dataclasses import dataclass, field
from typing import List, Dict, Any

from app.models.trustrepo_context import TrustRepoContext
from app.models.repository_context import RepositoryContext
from app.services.analysis.document_understanding_pipeline import DocumentUnderstandingPipeline
from app.services.code.pipeline.code_understanding_pipeline import CodeUnderstandingPipeline
from app.services.pipelines.knowledge_graph_pipeline import KnowledgeGraphPipeline
from app.services.pipelines.evidence_pipeline import EvidencePipeline
from app.services.pipelines.investigation_pipeline import InvestigationPipeline
from app.services.pipelines.verification_pipeline import VerificationPipeline
from app.services.pipelines.reporting_pipeline import ReportingPipeline


@dataclass
class LayerTrace:
    """Execution trace for a single pipeline layer."""
    layer: str
    status: str = "PENDING"       # PENDING | OK | FAILED | SKIPPED
    time_s: float = 0.0
    objects_created: int = 0
    evidence_count: int = 0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    memory_mb: float = 0.0
    cpu_percent: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "layer": self.layer,
            "status": self.status,
            "time_s": round(self.time_s, 3),
            "memory_mb": round(self.memory_mb, 2),
            "cpu_percent": round(self.cpu_percent, 1),
            "objects_created": self.objects_created,
            "evidence_count": self.evidence_count,
            "warnings": self.warnings,
            "errors": self.errors,
            "details": self.details,
        }


class TrustRepoPipeline:
    """
    Master Orchestrator for the TrustRepo Code Intelligence Platform.

    Features
    --------
    - Instruments every layer for execution time and object counts
    - Populates TrustRepoContext.execution_trace for the Runtime Dashboard
    - Implements Code Intelligence Mode when documentation is absent
    """

    def __init__(self):
        self.doc_pipeline = DocumentUnderstandingPipeline()
        self.code_pipeline = CodeUnderstandingPipeline()
        self.kg_pipeline = KnowledgeGraphPipeline()
        self.evidence_pipeline = EvidencePipeline()
        self.investigation_pipeline = InvestigationPipeline()
        self.verification_pipeline = VerificationPipeline()
        self.reporting_pipeline = ReportingPipeline()

    def run(self, repo_context: RepositoryContext) -> TrustRepoContext:
        print("==========================================")
        print("  TRUSTREPO PIPELINE v3.0")
        print("==========================================")

        context = TrustRepoContext(repository_context=repo_context)
        trace: List[LayerTrace] = []

        # ── Detect Mode ──────────────────────────────────────────────────────
        has_docs = bool(repo_context.documentation_files)
        code_intelligence_mode = not has_docs
        if code_intelligence_mode:
            print("\n  [Mode] CODE INTELLIGENCE — No documentation detected.")
            print("  [Mode] Pipeline will derive all insights from parser evidence.")
        else:
            print(
                f"\n  [Mode] DOCUMENTATION VERIFICATION — {
                    len(
                        repo_context.documentation_files)} doc files.")

        # ── Layer 2A: Document Understanding ─────────────────────────────────
        print("\n--- Layer 2A: Document Understanding ---")
        t = time.time()
        layer_trace = LayerTrace(layer="2A: Document Understanding")

        if code_intelligence_mode:
            print(
                "  [SKIPPED] Code Intelligence Mode — no documentation to process.")
            layer_trace.status = "SKIPPED"
            layer_trace.details["mode"] = "code_intelligence"
        else:
            try:
                doc_ctx = self.doc_pipeline.process(repo_context)
                context.document_context = doc_ctx
                context.claims = list(getattr(doc_ctx, 'claim_repository', []))
                layer_trace.status = "OK"
                layer_trace.objects_created = len(context.claims)
                layer_trace.details = {
                    "documents": len(doc_ctx.documents),
                    "claims": len(context.claims),
                }
                print(f"  Claims extracted: {len(context.claims)}")
            except Exception as e:
                layer_trace.status = "FAILED"
                layer_trace.errors.append(str(e))
                print(f"  [Layer 2A] Document pipeline failed: {e}")

        layer_trace.time_s = time.time() - t
        layer_trace.memory_mb = psutil.Process(
            os.getpid()).memory_info().rss / (1024 * 1024)
        layer_trace.cpu_percent = psutil.cpu_percent()
        trace.append(layer_trace)

        # ── Layer 2B: Code Understanding ─────────────────────────────────────
        print("\n--- Layer 2B: Code Understanding ---")
        t = time.time()
        layer_trace = LayerTrace(layer="2B: Code Understanding")
        try:
            code_ctx = self.code_pipeline.process(repo_context)
            context.code_context = code_ctx
            layer_trace.status = "OK"
            layer_trace.objects_created = len(code_ctx.symbols)
            layer_trace.details = {
                "source_files": len(code_ctx.source_files),
                "languages": len(code_ctx.detected_languages),
                "ast_nodes": len(code_ctx.ast_nodes),
                "symbols": len(code_ctx.symbols),
                "relationships": len(code_ctx.relationships),
            }
        except Exception as e:
            layer_trace.status = "FAILED"
            layer_trace.errors.append(str(e))
            print(f"  [Layer 2B] Code pipeline failed: {e}")

        layer_trace.time_s = time.time() - t
        layer_trace.memory_mb = psutil.Process(
            os.getpid()).memory_info().rss / (1024 * 1024)
        layer_trace.cpu_percent = psutil.cpu_percent()
        trace.append(layer_trace)

        # ── Layer 3: Knowledge Graph + Analytics ─────────────────────────────
        print("\n--- Layer 3: Knowledge Graph + Analytics ---")
        t = time.time()
        layer_trace = LayerTrace(layer="3: Knowledge Graph")
        try:
            context = self.kg_pipeline.run(context)
            graph = context.graph_context.graph
            layer_trace.status = "OK"
            layer_trace.objects_created = len(graph.nodes) if graph else 0
            layer_trace.evidence_count = len(
                context.semantic_context.evidence_chains)
            layer_trace.details = {
                "graph_nodes": len(graph.nodes) if graph else 0,
                "graph_edges": len(graph.edges) if graph else 0,
                "technologies": context.semantic_context.technologies,
                "technology_count": len(context.semantic_context.technologies),
                "features": context.semantic_context.features,
                "feature_count": len(context.semantic_context.features),
                "capabilities": context.semantic_context.capabilities,
                "capability_count": len(context.semantic_context.capabilities),
                "architectures": context.semantic_context.architectures,
                "schema_validation": context.graph_context.analytics.get("schema_validation", {}),
            }
        except Exception as e:
            layer_trace.status = "FAILED"
            layer_trace.errors.append(str(e))
            print(f"  [Layer 3] KG pipeline failed: {e}")

        layer_trace.time_s = time.time() - t
        layer_trace.memory_mb = psutil.Process(
            os.getpid()).memory_info().rss / (1024 * 1024)
        layer_trace.cpu_percent = psutil.cpu_percent()
        trace.append(layer_trace)

        # ── Code Intelligence Mode: Generate Repository Intelligence ─────────
        if code_intelligence_mode and context.graph_context.graph:
            self._generate_code_intelligence(context)

        # ── Layer 4: Evidence Retrieval ──────────────────────────────────────
        print("\n--- Layer 4: Evidence Retrieval ---")
        t = time.time()
        layer_trace = LayerTrace(layer="4: Evidence Retrieval")
        try:
            context = self.evidence_pipeline.run(context)
            layer_trace.status = "OK"
            layer_trace.objects_created = len(
                context.evidence_context.contexts)
            layer_trace.details = {
                "evidence_contexts": len(
                    context.evidence_context.contexts)}
        except Exception as e:
            layer_trace.status = "FAILED"
            layer_trace.errors.append(str(e))
            print(f"  [Layer 4] Evidence pipeline failed: {e}")

        layer_trace.time_s = time.time() - t
        layer_trace.memory_mb = psutil.Process(
            os.getpid()).memory_info().rss / (1024 * 1024)
        layer_trace.cpu_percent = psutil.cpu_percent()
        trace.append(layer_trace)

        # ── Layer 5: Multi-Agent Investigation + Reasoning ───────────────────
        print("\n--- Layer 5: Multi-Agent Investigation ---")
        t = time.time()
        layer_trace = LayerTrace(layer="5: Investigation")
        try:
            context = self.investigation_pipeline.run(context)
            layer_trace.status = "OK"
            layer_trace.objects_created = len(
                context.verification_context.verification_results)
        except Exception as e:
            layer_trace.status = "FAILED"
            layer_trace.errors.append(str(e))
            print(f"  [Layer 5] Investigation failed: {e}")

        layer_trace.time_s = time.time() - t
        layer_trace.memory_mb = psutil.Process(
            os.getpid()).memory_info().rss / (1024 * 1024)
        layer_trace.cpu_percent = psutil.cpu_percent()
        trace.append(layer_trace)

        # ── Layer 6: Verification Summary ────────────────────────────────────
        print("\n--- Layer 6: Verification Summary ---")
        t = time.time()
        layer_trace = LayerTrace(layer="6: Verification")
        try:
            context = self.verification_pipeline.run(context)
            layer_trace.status = "OK"
        except Exception as e:
            layer_trace.status = "FAILED"
            layer_trace.errors.append(str(e))
            print(f"  [Layer 6] Verification failed: {e}")

        layer_trace.time_s = time.time() - t
        layer_trace.memory_mb = psutil.Process(
            os.getpid()).memory_info().rss / (1024 * 1024)
        layer_trace.cpu_percent = psutil.cpu_percent()
        trace.append(layer_trace)

        # ── Layer 7: Report Generation ───────────────────────────────────────
        print("\n--- Layer 7: Report Generation ---")
        t = time.time()
        layer_trace = LayerTrace(layer="7: Report Generation")
        try:
            context = self.reporting_pipeline.run(context)
            layer_trace.status = "OK"
            layer_trace.details["report_generated"] = context.report_context.report is not None
        except Exception as e:
            layer_trace.status = "FAILED"
            layer_trace.errors.append(str(e))
            print(f"  [Layer 7] Reporting failed: {e}")

        layer_trace.time_s = time.time() - t
        layer_trace.memory_mb = psutil.Process(
            os.getpid()).memory_info().rss / (1024 * 1024)
        layer_trace.cpu_percent = psutil.cpu_percent()
        trace.append(layer_trace)

        # ── Store execution trace in context ─────────────────────────────────
        context.execution_trace = [t.to_dict() for t in trace]

        print("\n  Pipeline execution complete.")
        self._print_summary(trace, context)
        return context

    def _generate_code_intelligence(self, context: TrustRepoContext):
        """
        Code Intelligence Mode: Populate repository intelligence directly
        from graph evidence when no documentation is present.

        Generates:
        - detected_components (from Package + Class nodes)
        - missing_documentation (list of absent standard docs)
        - recommendations (from graph analytics: cycles, complexity)
        """
        graph = context.graph_context.graph
        if not graph:
            return

        # Detected components from Package and Class nodes
        components = []
        for node in graph.nodes:
            if node.label in ("Package", "Class"):
                name = node.properties.get("name", "")
                if name and name not in components:
                    components.append(name)

        context.code_intelligence = {
            "mode": "code_intelligence",
            "detected_components": sorted(components[:50]),
            "missing_documentation": [
                "README.md",
                "CONTRIBUTING.md",
                "CHANGELOG.md",
                "Architecture documentation",
            ],
            "recommendations": self._generate_recommendations(context),
        }
        print(
            f"  [Code Intelligence] {
                len(components)} components detected from graph.")
        print(
            f"  [Code Intelligence] {
                len(
                    context.code_intelligence['missing_documentation'])} documentation gaps found.")

    def _generate_recommendations(
            self, context: TrustRepoContext) -> List[str]:
        """Generate recommendations from graph analytics."""
        recs = []
        analytics = context.graph_context.analytics

        if analytics.get("cycle_detected"):
            count = analytics.get("cycle_count", 0)
            recs.append(
                f"Detected {count} dependency cycle(s). "
                "Refactor to remove circular imports and improve maintainability."
            )

        schema = analytics.get("schema_validation", {})
        if schema.get("isolated_nodes", 0) > 10:
            recs.append(
                f"{schema['isolated_nodes']} isolated graph nodes detected. "
                "These components have no relationships — consider integration or removal."
            )

        if schema.get("integrity_score", 1.0) < 0.8:
            recs.append(
                "Graph integrity score is below 80%. "
                "Some AST nodes are missing required properties. Run a code quality check."
            )

        techs = context.semantic_context.technologies
        if not techs:
            recs.append(
                "No technologies detected from parser evidence. "
                "Ensure dependency files (requirements.txt, package.json, pom.xml) are present."
            )

        if not recs:
            recs.append(
                "Repository structure appears healthy based on graph analysis.")

        return recs

    def _print_summary(
            self, trace: List[LayerTrace], context: TrustRepoContext):
        """Print a clean pipeline execution summary."""
        print("\n==========================================")
        print("  PIPELINE SUMMARY")
        print("==========================================")
        total_time = sum(t.time_s for t in trace)
        for t in trace:
            icon = "[OK]" if t.status == "OK" else (
                "[SKIP]" if t.status == "SKIPPED" else "[FAIL]")
            print(
                f"  {icon} {
                    t.layer:<30} {
                    t.time_s:.2f}s  objects={
                    t.objects_created}")
        print(f"\n  Total time: {total_time:.2f}s")
        print(f"  Technologies: {len(context.semantic_context.technologies)}")
        print(f"  Features:     {len(context.semantic_context.features)}")
        print(f"  Capabilities: {len(context.semantic_context.capabilities)}")
        print("==========================================")
