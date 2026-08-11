from typing import List
from app.models.knowledge.feature_instance import FeatureInstance
from app.repositories.graph_repository import GraphRepository
from app.services.knowledge.semantic_registry import SEMANTIC_REGISTRY


class GraphEnrichmentEngine:
    """
    Enriches the Neo4j Knowledge Graph with Semantic Features.
    (Technology) -[:ENABLES]-> (FeatureInstance) -[:IMPLEMENTS]-> (Capability)
    """

    def __init__(self, repo: GraphRepository = None):
        self.repo = repo or GraphRepository()

    def enrich(self, features: List[FeatureInstance]):
        print(
            f"  [GraphEnrichment] Persisting {
                len(features)} feature instances to graph...")

        for feat in features:
            def_node = SEMANTIC_REGISTRY.get_by_id(feat.definition_id)
            if not def_node:
                continue

            # Create the FeatureInstance node
            query = """
            MERGE (fi:FeatureInstance {id: $id})
            SET fi.canonical_name = $name,
                fi.definition_id = $def_id,
                fi.category = $category,
                fi.confidence = $confidence
            """
            params = {
                "id": feat.id,
                "name": feat.canonical_name,
                "def_id": feat.definition_id,
                "category": def_node.category,
                "confidence": feat.confidence
            }
            self.repo.conn.query(query, params)

            # Connect Capabilities
            for cap in def_node.capabilities:
                cap_query = """
                MATCH (fi:FeatureInstance {id: $id})
                MERGE (c:Capability {name: $cap})
                MERGE (fi)-[:IMPLEMENTS]->(c)
                """
                self.repo.conn.query(cap_query, {"id": feat.id, "cap": cap})

            # Connect to Evidence Nodes (Annotations, Files, etc.)
            for chain in feat.evidence:
                for item in chain.sequence:
                    if item.graph_node_id:
                        ev_query = """
                        MATCH (fi:FeatureInstance {id: $id})
                        MATCH (n) WHERE id(n) = $node_id
                        MERGE (fi)-[:SUPPORTED_BY]->(n)
                        """
                        try:
                            # graph_node_id is usually stringified integer ID
                            # in neo4j
                            node_id = int(item.graph_node_id)
                            self.repo.conn.query(
                                ev_query, {"id": feat.id, "node_id": node_id})
                        except (ValueError, TypeError):
                            pass

            # Connect from Technology (Optional if we mapped it explicitly in features,
            # but currently technologies list might be empty. If provided by
            # fusion, use it).
            for tech in feat.technologies:
                tech_query = """
                MATCH (fi:FeatureInstance {id: $id})
                MERGE (t:Technology {name: $tech})
                MERGE (t)-[:ENABLES]->(fi)
                """
                self.repo.conn.query(tech_query, {"id": feat.id, "tech": tech})
