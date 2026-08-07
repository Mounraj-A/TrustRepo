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
        
        verdict_str = message.payload.get("verdict", "INSUFFICIENT_EVIDENCE")
        
        # Map to VerificationVerdict Enum
        mapping = {
            "VERIFIED": VerificationVerdict.VERIFIED,
            "CONTRADICTION": VerificationVerdict.REFUTED,
            "MISSING_DOCUMENTATION": VerificationVerdict.INSUFFICIENT_EVIDENCE,
            "UNSUPPORTED_DOCUMENTATION": VerificationVerdict.INSUFFICIENT_EVIDENCE,
            "PARTIAL_DOCUMENTATION": VerificationVerdict.PARTIALLY_VERIFIED,
        }
        verdict = mapping.get(verdict_str, VerificationVerdict.INSUFFICIENT_EVIDENCE)
        
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
            reasoning_trace=decision_trace
        )
        
        message.payload["verification_result"] = result
        self._log(message, f"Verification complete. Verdict: {verdict.value}")
        
        message.route_to_next()
        return message
