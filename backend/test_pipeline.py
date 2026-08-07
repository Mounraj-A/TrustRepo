import os
from app.services.trustrepo_pipeline import TrustRepoPipeline
from app.services.ingestion.repository_scanner import RepositoryScanner
from app.models.repository_context import RepositoryContext

def test_pipeline():
    repo_path = os.path.abspath("repositories/Accounting_System")
    print(f"Running verification on {repo_path}")
    
    scanner = RepositoryScanner()
    
    # We need to construct a RepositoryContext and set source_code_files
    repo_context = RepositoryContext(repository_path=repo_path)
    scan_results = scanner.scan_repository(repo_path)
    repo_context.source_code_files = scan_results.get("source_code", [])
    repo_context.build_files = scan_results.get("build_files", [])
    repo_context.package_manifests = scan_results.get("package_manifests", [])
    
    pipeline = TrustRepoPipeline()
    trust_context = pipeline.run(repo_context)
    
    print("\n--- Final Context ---")
    print("Claims:", len(trust_context.claims))
    print("Graph Nodes:", len(trust_context.graph_context.graph.nodes) if trust_context.graph_context.graph else 0)
    print("Graph Edges:", len(trust_context.graph_context.graph.edges) if trust_context.graph_context.graph else 0)
    print("Technologies:", trust_context.semantic_context.technologies)
    print("Features:", trust_context.semantic_context.features)
    print("Capabilities:", trust_context.semantic_context.capabilities)
    print("Architecture:", trust_context.semantic_context.architectures)
    print("\n--- Trust Report ---")
    if hasattr(trust_context, 'trust_report') and trust_context.trust_report:
        print(trust_context.trust_report.model_dump_json(indent=2))
    else:
        print("No trust report generated.")

if __name__ == "__main__":
    test_pipeline()
