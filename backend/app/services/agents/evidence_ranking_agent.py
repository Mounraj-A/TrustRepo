from app.services.agents.base_agent import BaseAgent, AgentMessage, AgentRole
from app.models.knowledge.evidence import EvidenceChain, EvidenceStrength


class EvidenceRankingAgent(BaseAgent):
    """
    Evaluates raw evidence chains from the specialized agents, assigns an internal
    quality score based on evidence strength and path centrality, and sorts them.
    """
    role = AgentRole.EVIDENCE_RANKING

    def process(self, message: AgentMessage) -> AgentMessage:
        self._log(message, "Ranking evidence from all streams...")

        # Deserialize evidence chains (if they are passed as dicts in payload
        # or use message.evidence)
        all_chains = message.evidence
        if not all_chains:
            # Maybe they were passed in payload from Task Planner orchestration
            raw_code = message.payload.get("code_evidence", [])
            raw_doc = message.payload.get("doc_evidence", [])
            raw_graph = message.payload.get("graph_evidence", [])

            for item in raw_code + raw_doc + raw_graph:
                if isinstance(item, dict):
                    all_chains.append(EvidenceChain(**item))
                else:
                    all_chains.append(item)

        # Apply ranking heuristic
        scored_chains = []
        for chain in all_chains:
            score = 0.0

            # Base score by source engine / type
            if chain.chain_type == "Graph Analytics":
                score += 3.0
            elif chain.chain_type == "Semantic Feature":
                score += 2.0
            elif chain.chain_type == "Graph Traversal":
                score += 2.5
            elif chain.chain_type == "Documentation Match":
                score += 1.0

            # Score by sequence strength
            for item in chain.sequence:
                if item.evidence_strength == EvidenceStrength.PRIMARY:
                    score += 2.0
                elif item.evidence_strength == EvidenceStrength.SECONDARY:
                    score += 1.0
                elif item.evidence_strength == EvidenceStrength.TERTIARY:
                    score += 0.5

            scored_chains.append((score, chain))

        # Sort descending by score
        scored_chains.sort(key=lambda x: x[0], reverse=True)
        ranked_chains = [c for s, c in scored_chains]

        # Update message
        message.evidence = ranked_chains
        message.payload["ranked_evidence"] = [c.dict() for c in ranked_chains]

        self._log(
            message, f"Ranked {
                len(ranked_chains)} evidence chains. Top score: {
                scored_chains[0][0] if scored_chains else 0.0}")

        message.route_to_next()
        return message
