from app.services.agents.base_agent import BaseAgent, AgentMessage, AgentRole
from app.models.knowledge.evidence import EvidenceStrength

class EvidenceValidationAgent(BaseAgent):
    """
    Validates fused evidence chains before reasoning.
    Drops evidence that does not meet minimum quality thresholds (e.g. requires at least one PRIMARY evidence).
    Passes validated evidence forward.
    """
    role = AgentRole.EVIDENCE_VALIDATION

    def process(self, message: AgentMessage) -> AgentMessage:
        self._log(message, "Validating evidence chains for sufficient strength.")
        
        fused_evidence = message.evidence
        if not fused_evidence:
            self._log(message, "No evidence to validate.")
            message.route_to_next()
            return message
            
        validated_chains = []
        dropped_count = 0
        
        for chain in fused_evidence:
            has_primary = False
            for item in chain.sequence:
                if item.evidence_strength == EvidenceStrength.PRIMARY:
                    has_primary = True
                    break
            
            # For this validation, we require at least one PRIMARY evidence item in the chain
            # or a high enough confidence/ranking_score
            if has_primary or chain.ranking_score > 0.8:
                validated_chains.append(chain)
            else:
                dropped_count += 1
                
        message.evidence = validated_chains
        message.payload["validated_evidence_count"] = len(validated_chains)
        
        self._log(message, f"Validated {len(validated_chains)} chains. Dropped {dropped_count} weak chains.")
        
        message.route_to_next()
        return message
