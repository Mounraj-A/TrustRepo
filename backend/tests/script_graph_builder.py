from app.models.code.code_context import CodeContext
from app.services.knowledge.graph_builder import GraphBuilder

def test_graph_builder_memory_model():
    """
    Tests that the GraphBuilder correctly converts a CodeContext
    into a RepositoryKnowledgeGraph memory model.
    """
    # 1. Mock a CodeContext
    context = CodeContext()
    
    # Mock some extracted symbols
    context.symbols = [
        {"name": "main", "type": "Function", "qualname": "main.py:main", "file": "main.py", "start_line": 10},
        {"name": "calculate", "type": "Function", "qualname": "utils.py:calculate", "file": "utils.py", "start_line": 5},
        {"name": "App", "type": "Class", "qualname": "main.py:App", "file": "main.py", "start_line": 20}
    ]
    
    # Mock some extracted relationships
    context.relationships = [
        {"source": "main.py:main", "target": "utils.py:calculate", "type": "CALLS"},
        {"source": "main.py:App", "target": "main.py:main", "type": "DEFINES"}
    ]
    
    # 2. Build the graph model
    builder = GraphBuilder()
    graph = builder.build(context)
    
    # 3. Print the Expected Output
    print("=== EXPECTED OUTPUT: REPOSITORY KNOWLEDGE GRAPH ===")
    print(f"Total Nodes: {len(graph.nodes)}")
    for node in graph.nodes:
        print(f" - [{node.label}] {node.properties.get('name')} (ID: {node.properties.get('qualname')})")
        
    print(f"\nTotal Edges: {len(graph.edges)}")
    for edge in graph.edges:
        print(f" - {edge.source_qualname} -[{edge.rel_type}]-> {edge.target_qualname}")
        
    print("===================================================")

if __name__ == "__main__":
    test_graph_builder_memory_model()
