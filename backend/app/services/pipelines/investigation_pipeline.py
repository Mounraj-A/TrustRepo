"""
Investigation Pipeline — Layer 5 (Multi-Agent Reasoning)

Full wiring order:
    NormalizedClaim
        ↓
    TaskPlannerAgent  →  [CodeAgent | DocumentationAgent | KnowledgeGraphAgent]
        ↓
    EvidenceFusionAgent  (aggregates raw evidence dicts from all 3 agents)
        ↓
    EvidenceFusionEngine  (4-stream deduplication + ranking → unified EvidenceChains)
        ↓
    EvidenceValidationEngine  (false positive removal + completeness check)
        ↓
    ReasoningAgent  (Ontology → Quality → Decision Matrix → Confidence → Verdict)
        ↓
    VerificationEngine  (wraps result into VerificationResult with trust score)
"""
from app.models.trustrepo_context import TrustRepoContext
from app.models.knowledge.evidence import EvidenceChain
from app.models.knowledge.investigation import VerificationVerdict, VerificationResult
from app.services.analysis.claim_normalization_layer import ClaimNormalizationLayer
from app.services.agents.task_planner_agent import TaskPlannerAgent
from app.models.claim import Claim


class InvestigationPipeline:
    def __init__(self):
        self.normalizer = ClaimNormalizationLayer()

    def run(self, context: TrustRepoContext) -> TrustRepoContext:
        # Extract raw documentation text once for all claims
        raw_doc_text = ""
        if context.document_context and hasattr(context.document_context, 'documents'):
            raw_doc_text = " ".join(
                [d.content for d in context.document_context.documents]
            ).lower()

        # Create a fresh TaskPlannerAgent with the repository's documentation
        planner = TaskPlannerAgent(raw_doc_text=raw_doc_text)

        print(f"  Normalizing {len(context.claims)} claims...")

        # Step 1: Full claim normalization (deduplication + intent + features)
        normalized_claims = self.normalizer.normalize(context.claims)

        print(f"  {len(normalized_claims)} unique normalized claims after deduplication.")

        # Retrieve pre-collected evidence contexts (from EvidencePipeline Layer 4)
        pre_collected = context.evidence_context.contexts  # Dict[claim_id, EvidenceContext]

        # Retrieve technology evidence chains from context
        tech_chains: list = context.semantic_context.evidence_chains

        verified = 0
        refuted = 0
        partial = 0
        insufficient = 0

        # Step 2: For each normalized claim, run the full multi-agent pipeline
        for nc in normalized_claims:
            print(f"    Investigating: intent='{nc.intent}' features={nc.expected_features}")
            
            dummy_claim = Claim(
                id=nc.claim_id,
                text=nc.raw_text,
                source_document="documentation",
                source_section="auto",
            )

            try:
                # ── Agent Layer: Task Planner orchestrates the entire pipeline ─────────────
                final_message = planner.plan_and_execute(dummy_claim)
                
                if not final_message:
                    continue

                # Retrieve the final VerificationResult
                verification_result: VerificationResult = final_message.payload.get("verification_result")
                
                if verification_result:
                    context.verification_context.verification_results[nc.claim_id] = verification_result
                    verdict = verification_result.verdict
                else:
                    raise Exception("TaskPlannerAgent returned no VerificationResult.")

            except Exception as e:
                import traceback
                print(f"      Investigation failed for claim '{nc.claim_id}': {e}")
                traceback.print_exc()
                from datetime import datetime, timezone
                context.verification_context.verification_results[nc.claim_id] = VerificationResult(
                    claim_id=nc.claim_id,
                    verdict=VerificationVerdict.INSUFFICIENT_EVIDENCE,
                    trust_score=0.0,
                    reasoning_trace=[f"Investigation error: {e}"],
                    verification_timestamp=datetime.now(timezone.utc),
                )
                insufficient += 1
                continue

            if verdict == VerificationVerdict.VERIFIED:
                verified += 1
            elif verdict == VerificationVerdict.REFUTED:
                refuted += 1
            elif verdict == VerificationVerdict.PARTIALLY_VERIFIED:
                partial += 1
            else:
                insufficient += 1

        print(
            f"  Investigation complete: {verified} verified, {refuted} refuted, "
            f"{partial} partial, {insufficient} insufficient."
        )
        return context
