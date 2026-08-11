from app.repositories.graph_repository import GraphRepository


class CallGraphBuilder:
    """
    Computes graph metrics for function calls, treating them as derived properties
    rather than modifying the raw graph.
    """

    def __init__(self, repo: GraphRepository = None):
        self.repo = repo or GraphRepository()

    def build(self):
        # Calculate In-Degree (Core Utilities)
        self.repo.conn.query("""
        MATCH (f:Function)
        OPTIONAL MATCH ()-[r:CALLS]->(f)
        WITH f, count(r) as in_degree
        SET f.in_degree = in_degree
        """)

        # Calculate Out-Degree (Orchestrators)
        self.repo.conn.query("""
        MATCH (f:Function)
        OPTIONAL MATCH (f)-[r:CALLS]->()
        WITH f, count(r) as out_degree
        SET f.out_degree = out_degree
        """)
