"""
Code Agent — searches the Knowledge Graph for code-level evidence.
Specialization: code symbols, annotations, imports, method calls.
"""
from typing import List
from app.services.agents.base_agent import BaseAgent, AgentMessage, AgentRole
from app.models.knowledge.evidence import EvidenceChain, EvidenceItem, EvidenceSource, EvidenceStrength
from app.repositories.graph_repository import GraphRepository


class CodeAgent(BaseAgent):
    """
    Searches the Neo4j Knowledge Graph for code-level evidence
    (classes, methods, annotations, imports) matching the claim's expected features.
    """
    role = AgentRole.CODE

    def __init__(self):
        self.repo = GraphRepository()

    def process(self, message: AgentMessage) -> AgentMessage:
        features = message.expected_features
        self._log(
            message,
            f"Searching code graph for feature instances: {features}")

        evidence_chains = []
        for feat in features:
            results = self._query_feature_instances(feat)
            evidence_chains.extend(results)

        message.evidence.extend(evidence_chains)
        message.payload["code_evidence"] = [e.dict() for e in evidence_chains]
        message.confidence = min(
            0.3 + (len(evidence_chains) * 0.15), 0.95) if evidence_chains else 0.1
        self._log(
            message, f"Found {
                len(evidence_chains)} code evidence chains from semantic features.")
        message.route_to_next()
        return message

    def _query_feature_instances(self, feat_id: str) -> List[EvidenceChain]:
        query = """
        MATCH (fi:FeatureInstance)
        WHERE fi.definition_id = $feat
        OPTIONAL MATCH (fi)-[:SUPPORTED_BY]->(n)
        RETURN fi.id as id, fi.canonical_name as name, fi.confidence as confidence,
               collect({name: n.name, label: labels(n)[0], file: n.file_path, line: n.start_line}) as supporting_nodes
        LIMIT 5
        """
        try:
            results = self.repo.conn.query(query, {"feat": feat_id})
            chains = []
            for r in (results or []):
                items = []
                for node in r.get('supporting_nodes', []):
                    if node.get('name'):
                        items.append(
                            EvidenceItem(
                                source=EvidenceSource(
                                    file_path=node.get('file') or "unknown"),
                                context_type=node.get('label') or "Code",
                                evidence_strength=EvidenceStrength.PRIMARY if r.get(
                                    'confidence', 0) > 0.8 else EvidenceStrength.SECONDARY
                            )
                        )
                if items:
                    chain = EvidenceChain(
                        chain_id=f"code_feat_{r.get('id')}",
                        chain_type="Semantic Feature",
                        reasoning_trace=f"FeatureInstance({r.get('name')}) supports intent.",
                        sequence=items
                    )
                    chains.append(chain)
            return chains
        except Exception:
            return []
