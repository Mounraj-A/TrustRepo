from app.services.agents.base_agent import BaseAgent, AgentMessage, AgentRole

class EvidenceAgreementEngine(BaseAgent):
    """
    Quantifies cross-source agreement. A feature is 'Strongly Supported' if it has
    evidence from multiple independent sources (e.g., Code AND Documentation).
    """
    role = AgentRole.EVIDENCE_AGREEMENT

    def process(self, message: AgentMessage) -> AgentMessage:
        self._log(message, "Calculating cross-source agreement.")
        
        evidence_chains = message.evidence
        if not evidence_chains:
            message.payload["agreement_score"] = 0.0
            message.route_to_next()
            return message
            
        feature_sources = {}
        for chain in evidence_chains:
            # Extract feature ID if present (e.g., doc_feat_JWT -> JWT)
            parts = chain.chain_id.split("_feat_")
            if len(parts) == 2:
                feat = parts[1]
                source_type = parts[0]  # code, doc, or kg
                
                if feat not in feature_sources:
                    feature_sources[feat] = set()
                feature_sources[feat].add(source_type)
                
        # Calculate agreement
        total_features = len(message.expected_features)
        if total_features == 0:
            agreement_ratio = 1.0
        else:
            agreed_features = 0
            for feat in message.expected_features:
                sources = feature_sources.get(feat, set())
                if len(sources) > 1:
                    agreed_features += 1
            agreement_ratio = agreed_features / total_features
            
        message.payload["agreement_score"] = agreement_ratio
        message.payload["feature_sources"] = {k: list(v) for k, v in feature_sources.items()}
        
        # Boost confidence based on agreement
        bonus = agreement_ratio * 0.2
        message.confidence = min(message.confidence + bonus, 1.0)
        
        self._log(message, f"Cross-source agreement score: {agreement_ratio:.2f}")
        
        message.route_to_next()
        return message
