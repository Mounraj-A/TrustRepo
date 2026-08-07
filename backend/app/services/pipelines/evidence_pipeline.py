from app.models.trustrepo_context import TrustRepoContext
from app.services.analysis.evidence_collector import EvidenceCollector

class EvidencePipeline:
    def __init__(self):
        self.collector = EvidenceCollector()
        
    def run(self, context: TrustRepoContext) -> TrustRepoContext:
        for claim in context.claims:
            evidence_context = self.collector.collect(claim)
            context.evidence_context.contexts[claim.id] = evidence_context
        
        print(f"Evidence collected for {len(context.evidence_context.contexts)} claims.")
        return context
