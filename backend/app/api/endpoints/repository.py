"""
Repository API Endpoints

POST /repositories/analyze
    - Accepts repository_url
    - Runs the full TrustRepo pipeline
    - Returns RepositoryTrustReport as JSON + Markdown + graph metrics + code metrics
"""
from fastapi import APIRouter
from pydantic import BaseModel
import time
import logging

from app.services.ingestion.repository_ingestion_pipeline import RepositoryIngestionPipeline
from app.services.trustrepo_pipeline import TrustRepoPipeline
from app.services.reporting.report_generator import ReportGenerator

router = APIRouter(prefix="/repositories", tags=["Repositories"])
logger = logging.getLogger(__name__)


class AnalyzeRequest(BaseModel):
    repository_url: str


@router.get("/")
def list_repositories():
    return {"message": "TrustRepo API is operational. POST /repositories/analyze to analyze a repository."}


@router.post("/analyze")
def analyze_repository(req: AnalyzeRequest):
    """
    Executes the complete TrustRepo pipeline on the provided repository URL.

    Pipeline executed:
        RepositoryIngestion → DocumentUnderstanding → CodeUnderstanding
        → KnowledgeGraph + GraphAnalytics → EvidencePipeline
        → InvestigationPipeline (4-stream Fusion + Validation + Reasoning)
        → VerificationPipeline → ReportingPipeline

    Returns the full RepositoryTrustReport as JSON + Markdown.
    """
    # ── Validation ────────────────────────────────────────────────────────────
    if not req.repository_url or not (req.repository_url.startswith("http") or req.repository_url.startswith("local://")):
        return {
            "status": "error",
            "message": "Invalid repository URL. Must start with http/https or local://."
        }

    start_time = time.time()
    logger.info(f"Starting analysis for: {req.repository_url}")

    # ── Layer 1: Repository Ingestion ─────────────────────────────────────────
    try:
        ingestion_pipeline = RepositoryIngestionPipeline()
        repo_context = ingestion_pipeline.ingest(req.repository_url)
    except Exception as e:
        logger.error(f"Clone failure: {e}")
        return {
            "status": "error",
            "message": "Unable to clone repository.",
            "detail": str(e)
        }

    # ── Layers 2-7: Master Pipeline ───────────────────────────────────────────
    try:
        trustrepo_pipeline = TrustRepoPipeline()
        context = trustrepo_pipeline.run(repo_context)
    except Exception as e:
        logger.error(f"Pipeline failure: {e}", exc_info=True)
        return {
            "status": "error",
            "message": "Analysis pipeline failed.",
            "detail": str(e)
        }

    # ── Validate Pipeline Output ──────────────────────────────────────────────
    if not context.code_context or not context.code_context.source_files:
        return {
            "status": "error",
            "message": "Repository contains no supported source files (Java, Python, JS, TS)."
        }

    # ── Generate Markdown Report ──────────────────────────────────────────────
    rg = ReportGenerator()
    report = context.report_context.report if context.report_context else None
    markdown = rg.to_markdown(report) if report else ""

    processing_time = round(time.time() - start_time, 2)

    # ── Extract Graph Metrics ─────────────────────────────────────────────────
    graph_nodes = len(context.graph_context.graph.nodes) if context.graph_context and context.graph_context.graph else 0
    graph_edges = len(context.graph_context.graph.edges) if context.graph_context and context.graph_context.graph else 0
    graph_analytics = context.graph_context.analytics if context.graph_context else {}

    # ── Extract Code Metrics ──────────────────────────────────────────────────
    code_meta = {}
    if context.code_context:
        code_meta = {
            "source_files": len(context.code_context.source_files) if getattr(context.code_context, "source_files", None) else 0,
            "parsed_files": len(context.code_context.parsed_files) if getattr(context.code_context, "parsed_files", None) else 0,
            "ast_nodes": len(context.code_context.ast_nodes) if getattr(context.code_context, "ast_nodes", None) else 0,
            "uir_files": len(context.code_context.intermediate_representation) if getattr(context.code_context, "intermediate_representation", None) else 0,
            "symbols": len(context.code_context.symbols) if getattr(context.code_context, "symbols", None) else 0,
            "relationships": len(context.code_context.relationships) if getattr(context.code_context, "relationships", None) else 0,
        }

    # ── Extract Claim Statistics ──────────────────────────────────────────────
    verification_results = context.verification_context.verification_results if context.verification_context else {}
    total_claims = len(verification_results)
    from app.models.knowledge.investigation import VerificationVerdict
    verified_count = sum(
        1 for r in verification_results.values()
        if r.verdict == VerificationVerdict.VERIFIED
    )
    refuted_count = sum(
        1 for r in verification_results.values()
        if r.verdict == VerificationVerdict.REFUTED
    )
    partial_count = sum(
        1 for r in verification_results.values()
        if r.verdict == VerificationVerdict.PARTIALLY_VERIFIED
    )
    insufficient_count = total_claims - verified_count - refuted_count - partial_count

    logger.info(
        f"Analysis complete in {processing_time}s — "
        f"{total_claims} claims, {verified_count} verified, {refuted_count} refuted."
    )

    return {
        "status": "completed",
        "processing_time_seconds": processing_time,
        "report": report.model_dump() if report else {},
        "markdown": markdown,
        "code_metrics": {
            "source_files":   code_meta.get("source_files", 0),
            "parsed_files":   code_meta.get("parsed_files", 0),
            "ast_nodes":      code_meta.get("ast_nodes", 0),
            "uir_files":      code_meta.get("uir_files", 0),
            "symbols":        code_meta.get("symbols", 0),
            "relationships":  code_meta.get("relationships", 0),
        },
        "graph_metrics": {
            "nodes":          graph_nodes,
            "edges":          graph_edges,
            "technologies":   context.semantic_context.technologies if context.semantic_context else [],
            "architecture":   context.semantic_context.architectures if context.semantic_context else [],
            "analytics":      graph_analytics,
        },
        "verification_summary": {
            "total_claims":        total_claims,
            "verified":            verified_count,
            "refuted":             refuted_count,
            "partially_verified":  partial_count,
            "insufficient":        insufficient_count,
        }
    }