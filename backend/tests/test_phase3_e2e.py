import pytest
from app.models.claim import Claim
from app.models.trustrepo_context import TrustRepoContext
from app.models.repository_context import RepositoryContext
from app.services.pipelines.investigation_pipeline import InvestigationPipeline
from app.models.knowledge.investigation import VerificationVerdict

def test_phase3_investigation_pipeline_e2e():
    """
    End-to-End test for the Phase 3 Multi-Agent orchestration.
    """
    # 1. Setup mock context and dummy claims
    repo_ctx = RepositoryContext(repository_url="https://github.com/mock/repo", repository_name="mock-repo", repository_path="/tmp")
    context = TrustRepoContext(repository_context=repo_ctx)
    
    claim1 = Claim(
        id="mock-1",
        text="The auth service uses redis for caching",
        source_document="README.md",
        source_section="Architecture"
    )
    
    context.claims = [claim1]
    
    # We need to simulate DocumentContext and CodeContext so agents don't crash
    # For now, we mock the DocumentContext.
    class MockDocContext:
        documents = []
        metadata = {}
    context.document_context = MockDocContext()
    
    # 2. Run Investigation Pipeline
    pipeline = InvestigationPipeline()
    
    try:
        updated_context = pipeline.run(context)
        
        # 3. Verify results
        assert "mock-1" in updated_context.verification_results
        result = updated_context.verification_results["mock-1"]
        
        # Because we have no actual evidence streams returning matches, 
        # the outcome should be INSUFFICIENT_EVIDENCE or similar.
        assert result.verdict in [VerificationVerdict.INSUFFICIENT_EVIDENCE, VerificationVerdict.PARTIALLY_VERIFIED]
        
    except Exception as e:
        pytest.fail(f"Phase 3 Pipeline crashed: {e}")
