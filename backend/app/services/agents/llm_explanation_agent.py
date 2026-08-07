from app.services.agents.base_agent import BaseAgent, AgentMessage, AgentRole
from app.models.knowledge.investigation import VerificationResult

class LLMExplanationAgent(BaseAgent):
    """
    Consumes the deterministic VerificationResult and synthesizes a natural language
    explanation. This ensures the LLM is ONLY used for explanation, not for evaluation.
    """
    role = AgentRole.LLM_EXPLANATION

    def process(self, message: AgentMessage) -> AgentMessage:
        self._log(message, "Synthesizing natural language explanation.")
        
        result: VerificationResult = message.payload.get("verification_result")
        if not result:
            message.route_to_next()
            return message
            
        # Simulated LLM generation based strictly on deterministic inputs
        explanation = []
        explanation.append(f"The claim was evaluated and found to be {result.verdict.value} with {result.trust_score:.0f}% trust score.")
        
        if result.verdict.value == "VERIFIED":
            explanation.append("We found strong evidence in both the documentation and the codebase confirming this architecture.")
        elif result.verdict.value == "REFUTED":
            explanation.append("There is a direct contradiction between the documented architecture and the actual codebase implementation.")
        elif result.verdict.value == "INSUFFICIENT_EVIDENCE":
            explanation.append("We could not find sufficient code evidence to back up this documented claim.")
            
        synthetic_explanation = " ".join(explanation)
        
        # We attach the explanation to the result object
        result.reasoning_trace.append("Summary: " + synthetic_explanation)
        
        self._log(message, "Explanation synthesis complete.")
        
        message.route_to_next()
        return message
