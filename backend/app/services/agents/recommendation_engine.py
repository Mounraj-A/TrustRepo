from app.services.agents.base_agent import BaseAgent, AgentMessage, AgentRole

class RecommendationEngine(BaseAgent):
    """
    Analyzes coverage gaps and contradictions to generate actionable engineering recommendations.
    """
    role = AgentRole.RECOMMENDATION

    def process(self, message: AgentMessage) -> AgentMessage:
        self._log(message, "Generating engineering recommendations.")
        
        recommendations = []
        coverage = message.payload.get("coverage", {})
        
        # 1. Zombie Docs
        for z in coverage.get("zombie_docs", []):
            recommendations.append(f"Remove or update documentation for '{z}'; it is not found in the codebase.")
            
        # 2. Undocumented Features
        for u in coverage.get("undocumented", []):
            recommendations.append(f"Add documentation for '{u}'; it is implemented but not mentioned in the README.")
            
        # 3. Contradictions
        for c in message.payload.get("contradictions", []):
            if c.get("type") == "EVIDENCE_CLASH":
                recommendations.append(f"Resolve architectural contradiction regarding {c.get('feature')}: {c.get('description')}")
                
        message.payload["recommendations"] = recommendations
        
        self._log(message, f"Generated {len(recommendations)} recommendations.")
        
        message.route_to_next()
        return message
