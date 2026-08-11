from app.services.agents.base_agent import BaseAgent, AgentMessage, AgentRole


class CoverageAgent(BaseAgent):
    """
    Evaluates repository-wide documentation coverage logic.
    Identifies features that are implemented in code but undocumented,
    or documented but missing from code (zombie docs).
    """
    role = AgentRole.COVERAGE

    def process(self, message: AgentMessage) -> AgentMessage:
        self._log(message, "Evaluating feature coverage across sources.")

        feature_sources = message.payload.get("feature_sources", {})

        undocumented_features = []
        zombie_features = []
        fully_covered = []

        for feat in message.expected_features:
            sources = feature_sources.get(feat, [])
            has_code = "code" in sources or "kg" in sources
            has_docs = "doc" in sources

            if has_code and has_docs:
                fully_covered.append(feat)
            elif has_code and not has_docs:
                undocumented_features.append(feat)
            elif has_docs and not has_code:
                zombie_features.append(feat)

        message.payload["coverage"] = {
            "fully_covered": fully_covered,
            "undocumented": undocumented_features,
            "zombie_docs": zombie_features
        }

        if undocumented_features:
            self._log(
                message, f"Found {
                    len(undocumented_features)} undocumented features.")
        if zombie_features:
            self._log(
                message, f"Found {
                    len(zombie_features)} zombie documentations.")

        message.route_to_next()
        return message
