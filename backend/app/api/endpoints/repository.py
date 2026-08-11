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

def build_file_tree(source_files):
    tree = {"name": "root", "type": "directory", "children": {}}
    for f in source_files:
        parts = f.path.replace("\\", "/").split("/")
        current = tree
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                current["children"][part] = {
                    "name": part,
                    "type": "file",
                    "path": f.path,
                    "language": getattr(f, "language", ""),
                    "size": getattr(f, "size", 0)
                }
            else:
                if part not in current["children"]:
                    current["children"][part] = {
                        "name": part,
                        "type": "directory",
                        "children": {}
                    }
                current = current["children"][part]
    
    def dict_to_list(node):
        if "children" in node:
            node["children"] = [dict_to_list(c) for c in node["children"].values()]
            node["children"].sort(key=lambda x: (0 if x["type"] == "directory" else 1, x["name"]))
        return node
        
    res = dict_to_list(tree)
    return res.get("children", [])

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
    # ── Validation ──────────────────────────────────────────────────────────
    import os
    url = req.repository_url.strip()
    is_valid = (
        url.startswith("http")
        or url.startswith("local://")
        or os.path.isabs(url)
        or (len(url) > 2 and url[1] == ":")  # Windows drive letter: D:\...
    )
    if not url or not is_valid:
        return {
            "status": "error",
            "message": "Invalid repository URL. Must be http/https, a local:// URI, or an absolute local path."
        }

    start_time = time.time()
    logger.info(f"Starting analysis for: {req.repository_url}")

    # ── Layer 1: Repository Ingestion ───────────────────────────────────────
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

    # ── Layers 2-7: Master Pipeline ─────────────────────────────────────────
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

    # ── Validate Pipeline Output ────────────────────────────────────────────
    from fastapi import HTTPException
    
    # Check if any crucial pipeline layer failed
    if hasattr(context, 'execution_trace'):
        for trace in context.execution_trace:
            if trace.get("status") == "FAILED":
                failed_layer = trace.get("layer")
                errors = trace.get("errors", [])
                error_msg = errors[0] if errors else "Unknown error"
                raise HTTPException(
                    status_code=500, 
                    detail={
                        "status": "failed", 
                        "failed_stage": failed_layer, 
                        "error": error_msg
                    }
                )
                
    if not context.code_context or not context.code_context.source_files:
        return {
            "status": "error",
            "message": "Repository contains no supported source files (Java, Python, JS, TS)."
        }

    # ── Generate Markdown Report ────────────────────────────────────────────
    rg = ReportGenerator()
    report = context.report_context.report if context.report_context else None
    markdown = rg.to_markdown(report) if report else ""

    processing_time = round(time.time() - start_time, 2)

    # ── Extract Graph Metrics ───────────────────────────────────────────────
    graph_nodes = len(
        context.graph_context.graph.nodes) if context.graph_context and context.graph_context.graph else 0
    graph_edges = len(
        context.graph_context.graph.edges) if context.graph_context and context.graph_context.graph else 0
    graph_analytics = context.graph_context.analytics if context.graph_context else {}

    serialized_nodes = []
    serialized_edges = []
    if context.graph_context and context.graph_context.graph:
        for node in context.graph_context.graph.nodes:
            serialized_nodes.append({
                "id": str(node.properties.get("qualname", node.label)),
                "type": str(node.label),
                "name": str(node.properties.get("name", node.label)),
                **{k: v for k, v in node.properties.items() if k not in ["type", "name"]}
            })
        for edge in context.graph_context.graph.edges:
            serialized_edges.append({
                "source": str(edge.source_qualname),
                "target": str(edge.target_qualname),
                "type": str(edge.rel_type),
                **edge.properties
            })

    # ── Extract Code Metrics ────────────────────────────────────────────────
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

    # ── Extract Claim Statistics ────────────────────────────────────────────
    if report and hasattr(report, "verification_counts"):
        vc = report.verification_counts
        total_claims = vc.total_claims
        verified_count = vc.verified
        refuted_count = vc.contradicted
        partial_count = vc.partially_verified
        insufficient_count = vc.insufficient + vc.missing_documentation
    else:
        total_claims = 0
        verified_count = 0
        refuted_count = 0
        partial_count = 0
        insufficient_count = 0

    logger.info(
        f"Analysis complete in {processing_time}s — "
        f"{total_claims} claims, {verified_count} verified, {refuted_count} refuted."
    )

    return {
        "status": "completed",
        "processing_time_seconds": processing_time,
        "report": report.model_dump() if report else {},
        "markdown": markdown,

        # ── Code Metrics ─────────────────────────────────────────────────────
        "code_metrics": {
            "source_files": code_meta.get("source_files", 0),
            "parsed_files": code_meta.get("parsed_files", 0),
            "ast_nodes": code_meta.get("ast_nodes", 0),
            "uir_files": code_meta.get("uir_files", 0),
            "symbols": code_meta.get("symbols", 0),
            "relationships": code_meta.get("relationships", 0),
        },

        # ── Graph Metrics (all fields from semantic_context) ─────────────────
        "graph_metrics": {
            "nodes": graph_nodes,
            "edges": graph_edges,
            "raw_nodes": serialized_nodes,
            "raw_edges": serialized_edges,
            "technologies": context.semantic_context.technologies if context.semantic_context else [],
            "technology_categories": context.semantic_context.technology_categories if context.semantic_context else {},
            "features": context.semantic_context.features if context.semantic_context else [],
            "capabilities": context.semantic_context.capabilities if context.semantic_context else [],
            "architectures": context.semantic_context.architectures if context.semantic_context else [],
            "evidence_chain_count": len(context.semantic_context.evidence_chains) if context.semantic_context else 0,
            "analytics": graph_analytics,
            "schema_validation": graph_analytics.get("schema_validation", {}),
        },

        # ── Verification Summary ─────────────────────────────────────────────
        "verification_summary": {
            "total_claims": total_claims,
            "verified": verified_count,
            "refuted": refuted_count,
            "partially_verified": partial_count,
            "insufficient": insufficient_count,
        },

        # ── Phase 10: Runtime Dashboard — per-layer execution trace ──────────
        "execution_trace": context.execution_trace,

        # ── Phase 11: Code Intelligence Mode output ──────────────────────────
        "code_intelligence": context.code_intelligence,
        
        # ── File Tree ────────────────────────────────────────────────────────
        "file_tree": build_file_tree(context.code_context.source_files) if context.code_context and hasattr(context.code_context, "source_files") else [],
    }
