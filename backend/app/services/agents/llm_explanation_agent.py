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
            return message

        # Simulated LLM generation based strictly on deterministic inputs
        explanation = []
        explanation.append(
            f"The claim was evaluated and found to be {
                result.verdict.value} with {
                result.trust_score:.0f}% trust score.")

        if result.verdict.value == "VERIFIED":
            explanation.append(
                "We found strong evidence in both the documentation and the codebase confirming this architecture.")
        elif result.verdict.value == "CONTRADICTION":
            explanation.append(
                "There is a direct contradiction between the documented architecture and the actual codebase implementation.")
        elif result.verdict.value in ("MISSING_DOCUMENTATION", "UNSUPPORTED_DOCUMENTATION", "PARTIAL_DOCUMENTATION"):
            explanation.append(
                "We could not find sufficient matching code evidence to fully back up this documented claim, or the documentation is incomplete.")

        synthetic_explanation = " ".join(explanation)

        # PROMPT GUARD: Validate that the synthetic explanation does not alter the verdict
        # In a real LLM scenario, we would parse the LLM output and ensure it
        # matches the deterministic verdict.
        if result.verdict.value not in synthetic_explanation and "VERIFIED" not in synthetic_explanation and "REFUTED" not in synthetic_explanation and "MISSING" not in synthetic_explanation and "UNSUPPORTED" not in synthetic_explanation and "PARTIAL" not in synthetic_explanation:
            self._log(
                message,
                "PROMPT GUARD VIOLATION: Explanation did not reflect deterministic verdict. Overriding.")
            synthetic_explanation = f"Deterministic verdict: {
                result.verdict.value}."

        # We attach the explanation to the result object
        # Since ExplanationGenerator uses explanation, we can add it there or
        # just to trace
        message.payload["explanation"] = synthetic_explanation

        self._log(
            message,
            "Explanation synthesis complete with Prompt Guard verification.")

        return message
