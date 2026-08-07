from app.repositories.graph_repository import GraphRepository

class DependencyGraphBuilder:
    """
    Computes module dependency metrics without overwriting raw relationships.
    """
    def __init__(self, repo: GraphRepository = None):
        self.repo = repo or GraphRepository()

    def build(self):
        self.repo.conn.query("""
        MATCH (f:File)-[r:DEPENDS_ON]->(m)
        WITH f, count(r) as dependency_count
        SET f.dependency_score = dependency_count
        """)
