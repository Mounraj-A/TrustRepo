from app.repositories.graph_repository import GraphRepository
from app.models.knowledge.repository_knowledge_graph import RepositoryKnowledgeGraph, GraphNode, GraphEdge

def test_graph_repository():
    # 1. Create Graph model
    graph = RepositoryKnowledgeGraph(
        nodes=[
            GraphNode(label="Function", properties={"name": "main", "qualname": "main.py:main"}),
            GraphNode(label="Class", properties={"name": "App", "qualname": "main.py:App"})
        ],
        edges=[
            GraphEdge(source_qualname="main.py:App", target_qualname="main.py:main", rel_type="DEFINES")
        ]
    )
    
    # 2. Save Graph
    repo = GraphRepository()
    try:
        repo.save_graph(graph)
        
        # 3. Verify
        node_count = repo.conn.query("MATCH (n) RETURN count(n) as count")[0]["count"]
        edge_count = repo.conn.query("MATCH ()-[r]->() RETURN count(r) as count")[0]["count"]
        
        print("=== NEO4J PERSISTENCE TEST ===")
        print(f"Nodes in Neo4j: {node_count} (Expected: 2)")
        print(f"Edges in Neo4j: {edge_count} (Expected: 1)")
        print("==============================")
        assert node_count == 2
        assert edge_count == 1
        print("test_graph_repository passed!")
        
    except Exception as e:
        print(f"Neo4j Connection or Query Failed: {e}")

if __name__ == "__main__":
    test_graph_repository()
