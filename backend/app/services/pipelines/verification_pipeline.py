"""
VerificationPipeline — Layer 6

IMPORTANT: As of Phase 10, the InvestigationPipeline (Layer 5) now performs
verification inline via the VerificationEngine.verify(normalized_claim, agent_message)
call inside each claim's multi-agent investigation.

By the time this pipeline runs, context.verification_results is already populated.
This pipeline simply validates completeness and reports the final totals.
"""
from app.models.trustrepo_context import TrustRepoContext
from app.models.knowledge.investigation import VerificationVerdict


class VerificationPipeline:
    def __init__(self):
        pass

    def run(self, context: TrustRepoContext) -> TrustRepoContext:
        results = context.verification_context.verification_results

        if not results:
            print(
                "  No verification results found. Investigation pipeline may not have run.")
            return context

        verified = sum(
            1 for r in results.values()
            if r.verdict == VerificationVerdict.VERIFIED
        )
        refuted = sum(
            1 for r in results.values()
            if r.verdict == VerificationVerdict.CONTRADICTION
        )
        insufficient = len(results) - verified - refuted

        print(
            f"  Verification summary: {len(results)} claims — "
            f"{verified} verified, {refuted} refuted, {insufficient} insufficient."
        )
        return context
