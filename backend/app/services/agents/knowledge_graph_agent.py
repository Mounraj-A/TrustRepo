"""
Knowledge Graph Agent — runs structural graph queries for claim evidence.
Specialization: relationships, paths, dependencies, inheritance.
"""
from app.services.agents.base_agent import BaseAgent, AgentMessage, AgentRole
from app.models.knowledge.evidence import EvidenceCandidate, EvidenceChain, EvidenceItem, EvidenceSource, EvidenceStrength
from app.repositories.graph_repository import GraphRepository
from app.services.knowledge.graph_analytics_engine import GraphAnalyticsEngine


class KnowledgeGraphAgent(BaseAgent):
    """
    Runs structured Cypher queries on Neo4j to find relational evidence.
    Looks for IMPLEMENTS, INHERITS, DEPENDS_ON, ANNOTATED_WITH, IMPORTS relationships.
    """
    role = AgentRole.KNOWLEDGE_GRAPH

    def __init__(self):
        self.repo = GraphRepository()
        self.analytics = GraphAnalyticsEngine(repo=self.repo)

    def process(self, message: AgentMessage) -> AgentMessage:
        features = message.expected_features
        intent = message.payload.get("intent", "General")
        
        self._log(message, f"Running reasoning graph traversal for features: {features}")
        
        evidence_chains = []
        
        # 1. Fetch FeatureInstances matching the semantic features
        for feat in features:
            query = """
            MATCH (fi:FeatureInstance)-[:IMPLEMENTS]->(cap:Capability)
            WHERE fi.definition_id = $feat
            OPTIONAL MATCH (fi)-[:SUPPORTED_BY]->(n)
            RETURN fi.id as id, fi.canonical_name as name, cap.name as capability, collect(n.name) as supporting_nodes
            """
            results = self.repo.conn.query(query, {"feat": feat})
            if results:
                for r in results:
                    chain = EvidenceChain(
                        chain_id=f"kg_feat_{r.get('id')}",
                        chain_type="Graph Traversal",
                        reasoning_trace=f"Graph path: FeatureInstance({r.get('name')}) -> Capability({r.get('capability')})",
                        sequence=[
                            EvidenceItem(
                                source=EvidenceSource(file_path="Graph"),
                                context_type="Semantic Feature",
                                code_snippet=f"Supported by nodes: {r.get('supporting_nodes', [])}",
                                evidence_strength=EvidenceStrength.PRIMARY
                            )
                        ]
                    )
                    evidence_chains.append(chain)
                    
        # 2. Consume Graph Analytics Service (Centrality & Paths)
        analytics_report = self.analytics.run_full_analytics()
        
        # Find paths between capabilities or important nodes
        if len(features) > 1:
            for i in range(len(features) - 1):
                path = self.analytics.shortest_path(features[i], features[i+1])
                if path.reachable:
                    chain = EvidenceChain(
                        chain_id=f"kg_path_{features[i]}_{features[i+1]}",
                        chain_type="Graph Analytics",
                        reasoning_trace=f"Shortest path found between {features[i]} and {features[i+1]} (Length: {path.path_length})",
                        sequence=[]
                    )
                    evidence_chains.append(chain)
                    
        message.evidence.extend(evidence_chains)
        message.payload["graph_evidence"] = [e.dict() for e in evidence_chains]
        
        # Graph analytics centrality bonus
        critical_nodes = len(analytics_report.critical_nodes)
        bonus = min(critical_nodes * 0.05, 0.2)
        message.confidence = min(0.5 + (len(evidence_chains) * 0.1) + bonus, 1.0) if evidence_chains else 0.1
        
        self._log(message, f"Found {len(evidence_chains)} graph evidence chains. Critical nodes found: {critical_nodes}")
        
        message.route_to_next()
        return message
