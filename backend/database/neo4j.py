class MockNeo4jConnection:
    def query(self, query: str, parameters: dict = None):
        return []

neo4j_conn = MockNeo4jConnection()
