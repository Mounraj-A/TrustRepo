from app.models.claim import Claim
from app.models.claim_type import ClaimType
from app.services.analysis.evidence_collector import EvidenceCollector
from app.services.agents.investigator_agent import InvestigatorAgent
from app.services.verification.verification_engine import VerificationEngine

def test_phase4():
    claim = Claim(
        id="mock-1",
        text="The auth service uses redis for caching",
        source_document="README.md",
        source_section="Architecture",
        claim_type=ClaimType.DEPENDENCY
    )
    
    print("=== PHASE 4: VERIFICATION PIPELINE TEST ===")
    
    # 1. Collect Evidence & Investigate (Phase 3)
    agent = InvestigatorAgent()
    investigation = agent.investigate(claim)
    
    print(f"Agent Confidence: {investigation.confidence}")
    print(f"Missing Evidence: {investigation.missing_evidence}")
    print(f"Agent Recommended Action: {investigation.recommended_action}")
    
    # 2. Verify (Phase 4)
    engine = VerificationEngine()
    result = engine.verify(investigation)
    
    print("\n=== FINAL VERIFICATION RESULT ===")
    print(f"Claim ID: {result.claim_id}")
    print(f"Calculated Trust Score: {result.trust_score} / 100")
    print(f"Verdict: {result.verdict}")
    print(f"Total Supporting Evidence References: {len(result.supporting_evidence)}")
    print("Reasoning Trace Included:")
    for step in result.reasoning_trace:
        print(f" -> {step}")
    print("===========================================")

if __name__ == "__main__":
    test_phase4()
