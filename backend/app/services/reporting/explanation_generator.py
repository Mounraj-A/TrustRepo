"""
Explanation Generator

Translates a VerificationResult into a human-readable, evidence-backed ClaimReport.
Uses the new EvidenceChain provenance model (not the deprecated EvidenceProvenance).
"""
from app.models.knowledge.investigation import VerificationResult
from app.models.report.trust_report import ClaimReport, VerificationCategory


class ExplanationGenerator:
    """Translates VerificationResult into a readable ClaimReport."""

    def generate(self, result: VerificationResult, claim_text: str) -> ClaimReport:
        # 1. Format explanation from the deterministic reasoning trace
        explanation_lines = [
            f"The verification engine reached a verdict of **{result.verdict.value}** "
            f"with a trust score of {result.trust_score}/100.",
            "",
            "### Verification Reasoning Trace:",
        ]
        for step in result.reasoning_trace:
            explanation_lines.append(f"- {step}")

        explanation = "\n".join(explanation_lines)

        # 2. Pull provenance chain from supporting evidence if available
        provenance_chain = getattr(result, "provenance_chain", None)

        # 3. Build ClaimReport using the new schema
        return ClaimReport(
            claim_id=result.claim_id,
            claim_text=claim_text,
            verdict=result.verdict,
            verification_category=VerificationCategory.UNKNOWN,
            trust_score=result.trust_score,
            explanation=explanation,
            provenance_chain=provenance_chain,
            expected_features=result.expected_features,
            observed_features=result.observed_features,
            missing_features=result.missing_features,
            unsupported_features=result.unsupported_features,
            contradicted_features=result.contradicted_features,
            evidence_count=result.evidence_count,
            evidence_diversity=result.evidence_diversity,
            evidence_quality=result.evidence_quality,
            graph_connectivity=result.graph_connectivity,
            evidence_agreement=result.evidence_agreement
        )
