import os
from app.services.ingestion.repository_ingestion_pipeline import RepositoryIngestionPipeline
from app.services.trustrepo_pipeline import TrustRepoPipeline

def test_pipeline():
    # Since we are inside the project, let's use the actual project path.
    # However, RepositoryIngestionPipeline expects a URL to clone.
    # Let's bypass it for the test by using its internal components, or just use a dummy URL and let it fail to clone but we mock it.
    # Wait, if we use the backend folder, we can just instantiate RepositoryContext directly.
    from app.models.repository_context import RepositoryContext
    local_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    print("Collecting repository context...")
    repo_context = RepositoryContext(
        repository_url="local://trustrepo",
        repository_path=local_path,
        metadata={
            "commit_hash": "local-dev",
            "branch": "main"
        }
    )
    
    pipeline = TrustRepoPipeline()
    context = pipeline.run(repo_context)
    
    report = context.repository_report
    
    print("\n==========================================")
    print("TRUSTREPO PIPELINE OUTPUT")
    print("==========================================")
    
    print(f"\nRepository: {report.summary.repository_url}")
    print(f"Total Claims Extracted: {report.summary.total_claims}")
    print(f"Source Files Processed: {len(context.code_context.source_files) if context.code_context else 0}")
    print(f"Graph Nodes: {len(context.repository_graph.nodes) if context.repository_graph else 0}")
    print(f"Graph Edges: {len(context.repository_graph.edges) if context.repository_graph else 0}")
    
    total_evidence = sum(len(e.candidates) for e in context.evidence_contexts.values())
    print(f"Evidence Candidates: {total_evidence}")
    
    print(f"Verified Claims: {report.summary.verified_claims}")
    print(f"Refuted Claims: {report.summary.refuted_claims}")
    print(f"Insufficient Evidence: {report.summary.insufficient_claims}")
    
    print(f"Repository Trust Score: {report.summary.repository_trust_score}%")
    print("==========================================")
    
    from app.services.reporting.report_generator import ReportGenerator
    rg = ReportGenerator()
    print(rg.to_markdown(report))
    
if __name__ == "__main__":
    test_pipeline()
