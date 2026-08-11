from typing import List, Optional
from app.models.report.trust_report import ReasoningTrace, ReasoningStep
from app.models.knowledge.investigation import VerificationResult, VerificationVerdict
from app.models.claim import Claim

class ReasoningTraceBuilder:
    """
    Constructs an auditable trace of the reasoning steps that led to a specific verification verdict.
    It builds this strictly from the available evidence and the authoritative verification result,
    without altering or inferring verdicts.
    """

    def build_for_claim(
        self,
        claim: Claim,
        verification_result: VerificationResult
    ) -> ReasoningTrace:
        
        steps: List[ReasoningStep] = []
        step_counter = 1

        def next_id() -> str:
            nonlocal step_counter
            id_str = f"step-{step_counter:03d}"
            step_counter += 1
            return id_str

        # 1. Documentation Stage
        doc_step = ReasoningStep(
            step_id=next_id(),
            step_type="DOCUMENTATION",
            title="Documentation claim identified",
            description=claim.text,
            source=claim.source_document,
            source_file=claim.source_document
        )
        steps.append(doc_step)

        # 2. Repository Evidence Stage
        evidence_ids = []
        if verification_result.supporting_evidence:
            for ev in verification_result.supporting_evidence:
                if hasattr(ev, 'chain') and ev.chain and hasattr(ev.chain, 'sequence'):
                    for item in ev.chain.sequence:
                        if hasattr(item, 'id'):
                            evidence_ids.append(item.id)
                            
                            ev_step = ReasoningStep(
                                step_id=next_id(),
                                step_type="REPOSITORY_EVIDENCE",
                                title="Repository evidence found",
                                source_file=item.source.file_path if item.source else None,
                                line_start=item.source.line_number if item.source else None,
                                line_end=item.source.line_end if item.source else None,
                                evidence_ids=[item.id]
                            )
                            steps.append(ev_step)
        
        verdict = verification_result.verdict

        # 3. Evidence Comparison Stage based on the verdict
        if verdict == VerificationVerdict.VERIFIED:
            steps.append(ReasoningStep(
                step_id=next_id(),
                step_type="EVIDENCE_COMPARISON",
                title="Repository evidence supports the claim",
                evidence_ids=evidence_ids,
                result="SUPPORTED"
            ))
        elif verdict == VerificationVerdict.MISSING_DOCUMENTATION:
            steps.append(ReasoningStep(
                step_id=next_id(),
                step_type="DOCUMENTATION_CHECK",
                title="Documentation coverage check",
                description="No corresponding documentation statement was found for the discovered repository capability.",
                evidence_ids=evidence_ids,
                result="MISSING"
            ))
        elif verdict == VerificationVerdict.CONTRADICTION:
            steps.append(ReasoningStep(
                step_id=next_id(),
                step_type="EVIDENCE_COMPARISON",
                title="Repository evidence conflicts with claim",
                evidence_ids=evidence_ids,
                result="CONFLICT"
            ))
            steps.append(ReasoningStep(
                step_id=next_id(),
                step_type="CONTRADICTION_CHECK",
                title="Contradiction confirmed",
                evidence_ids=evidence_ids,
                result="CONTRADICTED"
            ))
        elif verdict == VerificationVerdict.PARTIAL_DOCUMENTATION or verdict == VerificationVerdict.UNSUPPORTED_DOCUMENTATION:
             steps.append(ReasoningStep(
                step_id=next_id(),
                step_type="EVIDENCE_COMPARISON",
                title="Repository evidence partially supports the claim",
                evidence_ids=evidence_ids,
                result="PARTIAL"
            ))
        else:
             steps.append(ReasoningStep(
                step_id=next_id(),
                step_type="EVIDENCE_COMPARISON",
                title="Evidence evaluation completed",
                evidence_ids=evidence_ids,
                result="INSUFFICIENT"
            ))

        # 4. Final Verdict Step
        steps.append(ReasoningStep(
            step_id=next_id(),
            step_type="VERDICT",
            title="Verification completed",
            result=verdict.value
        ))

        explanation = None
        if verification_result.reasoning_trace and len(verification_result.reasoning_trace) > 0:
            explanation = "\\n".join(verification_result.reasoning_trace)
        
        return ReasoningTrace(
            claim_id=claim.id,
            steps=steps,
            final_verdict=verdict,
            explanation=explanation
        )
