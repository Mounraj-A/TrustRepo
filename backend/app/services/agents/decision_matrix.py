from app.services.agents.base_agent import BaseAgent, AgentMessage, AgentRole
from app.services.verification.decision_matrix import DecisionMatrix as CoreDecisionMatrix

class DecisionMatrix(BaseAgent):
    """
    Wraps the core deterministic DecisionMatrix engine as an Agent in the pipeline.
    Produces the 5-state verdict based on Expected vs Observed features.
    """
    role = AgentRole.DECISION_MATRIX

    def __init__(self):
        self.engine = CoreDecisionMatrix()

    def process(self, message: AgentMessage) -> AgentMessage:
        self._log(message, "Applying Decision Matrix for final verdict.")
        
        expected = message.payload.get("expected_features_set", [])
        observed = message.payload.get("observed_features_set", [])
        
        # We can also pass contradictions into the evaluation, but the CoreDecisionMatrix
        # currently relies on known static pairs. Let's let it run its own or we can inject.
        
        result = self.engine.evaluate(expected, observed, message.payload.get("claim_text", ""))
        
        message.payload["verdict"] = result.final_verdict.value
        message.payload["decision_trace"] = result.reasoning_trace
        message.payload["coverage_score"] = result.coverage_score
        message.payload["consistency_score"] = result.consistency_score
        message.payload["expected_features"] = result.expected_features
        message.payload["observed_features"] = result.observed_features
        message.payload["missing_features"] = result.missing_features
        message.payload["unsupported_features"] = result.unsupported_features
        message.payload["contradicted_features"] = result.contradicted_features
        
        # Populate new reasoning metrics
        fused = message.payload.get("fused_evidence", [])
        message.payload["evidence_count"] = len(fused)
        
        types = set(e.get("chain_type", "") for e in fused)
        message.payload["evidence_diversity"] = min(len(types) * 0.25, 1.0)
        
        avg_quality = sum(e.get("confidence", 0.0) for e in fused) / max(len(fused), 1)
        message.payload["evidence_quality"] = avg_quality
        message.payload["graph_connectivity"] = message.payload.get("coverage_score", 0.0)
        message.payload["evidence_agreement"] = message.payload.get("consistency_score", 0.0)
        
        self._log(message, f"Decision Matrix verdict: {result.final_verdict.value}")
        
        message.route_to_next()
        return message
