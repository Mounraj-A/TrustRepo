from app.services.agents.base_agent import BaseAgent, AgentMessage, AgentRole

class ReasoningAgent(BaseAgent):
    """
    Reasoning Agent — Core logic for evaluating Expected vs Observed states.
    Uses conflicts and contradictions from previous stages to calculate a raw Reasoning Confidence.
    """
    role = AgentRole.REASONING

    def process(self, message: AgentMessage) -> AgentMessage:
        self._log(message, "Evaluating Expected vs Observed features.")
        
        expected = set(message.expected_features)
        
        # Determine Observed features from Evidence
        fused_evidence = message.payload.get("fused_evidence", [])
        observed = set()
        for ev in fused_evidence:
            parts = ev.get("chain_id", "").split("_feat_")
            if len(parts) == 2:
                observed.add(parts[1])
                
        # Calculate Expected vs Observed
        if not expected:
            ratio = 1.0
        else:
            intersection = expected.intersection(observed)
            ratio = len(intersection) / len(expected)
            
        message.payload["expected_features_set"] = list(expected)
        message.payload["observed_features_set"] = list(observed)
        message.payload["feature_ratio"] = ratio
        
        # Penalties from contradictions
        contradictions = message.payload.get("contradictions", [])
        penalty = 0.0
        for c in contradictions:
            if c.get("severity") == "HIGH":
                penalty += 0.3
            else:
                penalty += 0.15
                
        # Final Reasoning Confidence
        base_confidence = message.confidence
        reasoning_confidence = base_confidence * ratio - penalty
        reasoning_confidence = max(min(reasoning_confidence, 1.0), 0.0)
        
        message.payload["reasoning_confidence"] = reasoning_confidence
        message.confidence = reasoning_confidence
        
        self._log(message, f"Expected {len(expected)} features, Observed {len(observed)} features. Ratio: {ratio:.2f}")
        if penalty > 0:
            self._log(message, f"Applied contradiction penalty: -{penalty:.2f}")
        self._log(message, f"Final Reasoning Confidence: {reasoning_confidence:.2f}")
        
        message.route_to_next()
        return message
