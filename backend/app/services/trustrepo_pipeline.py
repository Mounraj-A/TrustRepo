"""
Master Orchestrator for the entire TrustRepo system.

Full pipeline execution order:
    Repository URL
        ↓  [Layer 1] RepositoryIngestionPipeline
    RepositoryContext
        ↓  [Layer 2A] DocumentUnderstandingPipeline
    DocumentContext → Claims
        ↓  [Layer 2B] CodeUnderstandingPipeline
    CodeContext → AST → UIR → Symbols → Relationships
        ↓  [Layer 3] KnowledgeGraphPipeline
    RepositoryKnowledgeGraph → Neo4j → GraphAnalytics → TechDetection → ArchDetection
        ↓  [Layer 4] EvidencePipeline
    EvidenceContext per Claim (from KG + Semantic + Code + Docs)
        ↓  [Layer 5] InvestigationPipeline
    EvidenceFusion → EvidenceValidation → ReasoningAgent → VerificationResult per Claim
        ↓  [Layer 6] VerificationPipeline
    Verification Summary
        ↓  [Layer 7] ReportingPipeline
    RepositoryTrustReport
"""
from app.models.trustrepo_context import TrustRepoContext
from app.models.repository_context import RepositoryContext
from app.services.analysis.document_understanding_pipeline import DocumentUnderstandingPipeline
from app.services.code.pipeline.code_understanding_pipeline import CodeUnderstandingPipeline
from app.services.pipelines.knowledge_graph_pipeline import KnowledgeGraphPipeline
from app.services.pipelines.evidence_pipeline import EvidencePipeline
from app.services.pipelines.investigation_pipeline import InvestigationPipeline
from app.services.pipelines.verification_pipeline import VerificationPipeline
from app.services.pipelines.reporting_pipeline import ReportingPipeline


class TrustRepoPipeline:
    """Master Orchestrator for the entire TrustRepo system."""

    def __init__(self):
        self.doc_pipeline          = DocumentUnderstandingPipeline()
        self.code_pipeline         = CodeUnderstandingPipeline()
        self.kg_pipeline           = KnowledgeGraphPipeline()
        self.evidence_pipeline     = EvidencePipeline()
        self.investigation_pipeline = InvestigationPipeline()
        self.verification_pipeline = VerificationPipeline()
        self.reporting_pipeline    = ReportingPipeline()

    def run(self, repo_context: RepositoryContext) -> TrustRepoContext:
        print("==========================================")
        print("  TRUSTREPO PIPELINE v2.0")
        print("==========================================")

        # Initialize the master context
        context = TrustRepoContext(repository_context=repo_context)

        # ── Layer 2A: Document Understanding ──────────────────────────────────
        print("\n--- Layer 2A: Document Understanding ---")
        try:
            doc_ctx = self.doc_pipeline.process(repo_context)
            context.document_context = doc_ctx
            # claim_repository is the final deduplicated list of Claim objects
            context.claims = list(getattr(doc_ctx, 'claim_repository', []))
            print(f"  Claims extracted: {len(context.claims)}")
        except Exception as e:
            print(f"  [Layer 2A] Document pipeline failed: {e}")

        # ── Layer 2B: Code Understanding ──────────────────────────────────────
        print("\n--- Layer 2B: Code Understanding ---")
        try:
            code_ctx = self.code_pipeline.process(repo_context)
            context.code_context = code_ctx
        except Exception as e:
            print(f"  [Layer 2B] Code pipeline failed: {e}")

        # ── Layer 3: Knowledge Graph + Analytics ──────────────────────────────
        print("\n--- Layer 3: Knowledge Graph + Analytics ---")
        context = self.kg_pipeline.run(context)

        # ── Layer 4: Evidence Retrieval ───────────────────────────────────────
        print("\n--- Layer 4: Evidence Retrieval ---")
        context = self.evidence_pipeline.run(context)

        # ── Layer 5: Multi-Agent Investigation + Reasoning ────────────────────
        print("\n--- Layer 5: Multi-Agent Investigation ---")
        context = self.investigation_pipeline.run(context)

        # ── Layer 6: Verification Summary ─────────────────────────────────────
        print("\n--- Layer 6: Verification Summary ---")
        context = self.verification_pipeline.run(context)

        # ── Layer 7: Report Generation ────────────────────────────────────────
        print("\n--- Layer 7: Report Generation ---")
        context = self.reporting_pipeline.run(context)

        print("\n  Pipeline execution complete.")
        return context
