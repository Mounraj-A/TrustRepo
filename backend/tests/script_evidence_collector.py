from app.models.claim import Claim
from app.models.claim_type import ClaimType
from app.services.analysis.evidence_collector import EvidenceCollector
from app.services.agents.investigator_agent import InvestigatorAgent

def test_phase3():
    claim = Claim(
        id="mock-1",
        text="The auth service uses redis for caching",
        source_document="README.md",
        source_section="Architecture",
        claim_type=ClaimType.DEPENDENCY
    )
    
    print("=== TESTING EVIDENCE COLLECTOR ===")
    collector = EvidenceCollector()
    context = collector.collect(claim)
    
    print(f"Claim: {context.claim.text}")
    print(f"Total Deduped Candidates Retrieved: {len(context.candidates)}")
    for c in context.candidates:
        print(f" - [{c.source_engine.upper()}] {c.content}")
        
    print("\n=== TESTING INVESTIGATOR AGENT (Memory) ===")
    agent = InvestigatorAgent()
    final_context = agent.investigate(claim)
    print(f"Agent Memory Key: {claim.id}")
    print(f"Evidence in Memory: {len(final_context.candidates)} candidates stored.")
    print("===========================================")

if __name__ == "__main__":
    test_phase3()
