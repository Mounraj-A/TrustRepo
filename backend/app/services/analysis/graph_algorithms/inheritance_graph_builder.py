from app.repositories.graph_repository import GraphRepository


class InheritanceGraphBuilder:
    """
    Calculates OOP metrics like Depth of Inheritance Tree (DIT).
    """

    def __init__(self, repo: GraphRepository = None):
        self.repo = repo or GraphRepository()

    def build(self):
        self.repo.conn.query("""
        MATCH (c:Class)
        OPTIONAL MATCH path = (c)-[:INHERITS_FROM*]->(base)
        WITH c, max(length(path)) as dit
        SET c.dit = coalesce(dit, 0)
        """)
