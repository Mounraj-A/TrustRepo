from app.models.code.code_context import CodeContext
from app.models.knowledge.repository_knowledge_graph import RepositoryKnowledgeGraph, GraphNode, GraphEdge

class GraphBuilder:
    """
    Builds the RepositoryKnowledgeGraph model from the CodeContext.
    It does not talk to Neo4j directly. It only produces the graph model.
    """
    def build(self, code_context: CodeContext) -> RepositoryKnowledgeGraph:
        graph = RepositoryKnowledgeGraph()
        
        # Build Nodes
        for sym in code_context.symbols:
            label = str(sym.type).capitalize()
            label = "".join([c for c in label if c.isalnum()]) or "Entity"
            
            props = {
                "name": sym.name,
                "qualname": sym.qualname,
                "file_path": sym.file_path,
                "start_line": sym.start_line
            }
            props.update(sym.properties)
            props = {k: v for k, v in props.items() if v is not None}
            
            graph.nodes.append(GraphNode(label=label, properties=props))
            
        # Build Edges
        for rel in code_context.relationships:
            source = rel.source_qualname
            target = rel.target_qualname
            rel_type = rel.type.upper()
            rel_type = "".join([c for c in rel_type if c.isalnum() or c == "_"])
            
            if source and target:
                graph.edges.append(GraphEdge(
                    source_qualname=source,
                    target_qualname=target,
                    rel_type=rel_type,
                    properties=rel.properties
                ))
                
        return graph
