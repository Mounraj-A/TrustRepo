from app.services.agents.base_agent import BaseAgent, AgentMessage, AgentRole


class ContradictionAgent(BaseAgent):
    """
    Analyzes fused evidence, conflicts, and coverage gaps to flag explicit semantic contradictions.
    Produces a list of formal Contradiction Objects.
    """
    role = AgentRole.CONTRADICTION

    def process(self, message: AgentMessage) -> AgentMessage:
        self._log(
            message,
            "Detecting explicit contradictions across evidence.")

        # 1. Gather conflicts from Fusion
        fusion_conflicts = message.payload.get("conflicts", [])

        # 2. Gather coverage gaps from Coverage
        coverage = message.payload.get("coverage", {})
        zombie_docs = coverage.get("zombie_docs", [])

        contradictions = []

        for c in fusion_conflicts:
            contradictions.append({
                "type": "EVIDENCE_CLASH",
                "feature": c.get("feature"),
                "description": c.get("description"),
                "severity": "HIGH"
            })

        for z in zombie_docs:
            contradictions.append({
                "type": "ZOMBIE_DOCUMENTATION",
                "feature": z,
                "description": f"Feature '{z}' is documented but no supporting code/graph evidence was found.",
                "severity": "MEDIUM"
            })

        message.payload["contradictions"] = contradictions

        if contradictions:
            self._log(
                message, f"Found {
                    len(contradictions)} contradictions. Confidence penalized.")
            message.confidence = max(message.confidence - 0.2, 0.1)

        message.route_to_next()
        return message
