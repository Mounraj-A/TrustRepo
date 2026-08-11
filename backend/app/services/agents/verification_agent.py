from app.services.agents.base_agent import BaseAgent, AgentMessage, AgentRole
from app.models.knowledge.investigation import VerificationVerdict, VerificationResult
from app.models.report.trust_report import VerificationCategory


class VerificationAgent(BaseAgent):
    """
    Packages the final results from the Decision Matrix and Recommendation Engine
    into a standardized VerificationResult.
    """
    role = AgentRole.VERIFICATION

    def process(self, message: AgentMessage) -> AgentMessage:
        self._log(message, "Packaging final Verification Result.")

        verdict_str = message.payload.get("verdict", "MISSING_DOCUMENTATION")

        # Map to VerificationVerdict Enum
        mapping = {
            "VERIFIED": VerificationVerdict.VERIFIED,
            "CONTRADICTION": VerificationVerdict.CONTRADICTION,
            "MISSING_DOCUMENTATION": VerificationVerdict.MISSING_DOCUMENTATION,
            "UNSUPPORTED_DOCUMENTATION": VerificationVerdict.UNSUPPORTED_DOCUMENTATION,
            "PARTIAL_DOCUMENTATION": VerificationVerdict.PARTIAL_DOCUMENTATION,
        }
        verdict = mapping.get(verdict_str,
                              VerificationVerdict.MISSING_DOCUMENTATION)

        # Determine category based on intent
        intent = message.payload.get("intent", "").lower()
        if "security" in intent or "auth" in intent:
            category = VerificationCategory.SECURITY
        elif "persistence" in intent or "database" in intent:
            category = VerificationCategory.DEPENDENCY
        elif "architecture" in intent or "microservice" in intent:
            category = VerificationCategory.ARCHITECTURE
        elif "interface" in intent or "api" in intent:
            category = VerificationCategory.BEHAVIORAL
        else:
            category = VerificationCategory.STRUCTURAL

        decision_trace = message.payload.get("decision_trace", "")
        if isinstance(decision_trace, str):
            decision_trace = [decision_trace] if decision_trace else []

        result = VerificationResult(
            claim_id=message.claim_id,
            verdict=verdict,
            trust_score=message.confidence * 100,  # Assuming confidence is 0-1
            supporting_evidence=[],  # This can be populated if needed
            reasoning_trace=decision_trace,
            expected_features=message.payload.get("expected_features", []),
            observed_features=message.payload.get("observed_features", []),
            missing_features=message.payload.get("missing_features", []),
            unsupported_features=message.payload.get(
                "unsupported_features", []),
            contradicted_features=message.payload.get(
                "contradicted_features", []),
            evidence_count=message.payload.get("evidence_count", 0),
            evidence_diversity=message.payload.get("evidence_diversity", 0.0),
            evidence_quality=message.payload.get("evidence_quality", 0.0),
            graph_connectivity=message.payload.get("graph_connectivity", 0.0),
            evidence_agreement=message.payload.get("evidence_agreement", 0.0)
        )

        message.payload["verification_result"] = result
        self._log(message, f"Verification complete. Verdict: {verdict.value}")

        message.route_to_next()
        return message
