from app.models.knowledge.investigation import VerificationResult, VerificationVerdict
from app.models.knowledge.evidence import EvidenceCandidate
from app.services.reporting.report_generator import ReportGenerator

def test_phase5():
    print("=== PHASE 5: TRUST REPORT GENERATION TEST ===\n")
    
    # 1. Mock output from Phase 4
    results = [
        VerificationResult(
            claim_id="mock-1",
            verdict=VerificationVerdict.VERIFIED,
            trust_score=95.0,
            reasoning_trace=[
                "Topological match found in Neo4j for 'AuthService' and 'Redis'.",
                "High confidence from Code Context evidence."
            ],
            supporting_evidence=[
                EvidenceCandidate(source_engine="graph", content="AuthService -[USES]-> Redis", metadata={"file_path": "graph_node:Redis"})
            ]
        ),
        VerificationResult(
            claim_id="mock-2",
            verdict=VerificationVerdict.REFUTED,
            trust_score=15.0,
            reasoning_trace=[
                "Evidence strongly contradicts the claim.",
                "Found MySQL used instead of PostgreSQL."
            ],
            supporting_evidence=[
                EvidenceCandidate(source_engine="code", content="conn = mysql.connect()", metadata={"file_path": "src/db.py"})
            ]
        ),
        VerificationResult(
            claim_id="mock-3",
            verdict=VerificationVerdict.INSUFFICIENT_EVIDENCE,
            trust_score=45.0,
            reasoning_trace=[
                "Missing critical evidence regarding API rate limits.",
                "Unable to verify claim based on available context."
            ],
            supporting_evidence=[]
        )
    ]
    
    claim_texts = {
        "mock-1": "The auth service uses redis for caching",
        "mock-2": "The system uses PostgreSQL for primary storage",
        "mock-3": "The API rate limits at 100 requests per minute"
    }
    
    repo_metadata = {
        "url": "https://github.com/mounraj/trustrepo",
        "commit_sha": "a1b2c3d4e5f6",
        "branch": "main",
        "technologies": ["Python", "FastAPI", "Neo4j"],
        "architecture": ["Microservices"]
    }
    
    # 2. Generate Report
    generator = ReportGenerator()
    report = generator.generate_report(results, claim_texts, repo_metadata)
    
    # 3. Output Markdown
    markdown_output = generator.to_markdown(report)
    print(markdown_output)

if __name__ == "__main__":
    test_phase5()
