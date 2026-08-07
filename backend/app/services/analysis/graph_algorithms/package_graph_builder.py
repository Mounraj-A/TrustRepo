from app.repositories.graph_repository import GraphRepository

class PackageGraphBuilder:
    """
    Computes hierarchical package/directory structure metrics.
    """
    def __init__(self, repo: GraphRepository = None):
        self.repo = repo or GraphRepository()

    def build(self):
        self.repo.conn.query("""
        MATCH (p:Package)-[:CONTAINS]->(f:File)
        WITH p, count(f) as file_count
        SET p.file_count = file_count
        """)
