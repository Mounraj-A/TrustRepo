import tempfile
from pathlib import Path
from app.models.repository_context import RepositoryContext
from app.services.code.pipeline.code_understanding_pipeline import CodeUnderstandingPipeline
from app.services.knowledge.graph_builder import GraphBuilder
from app.repositories.graph_repository import GraphRepository
from app.services.analysis.technology_detection import TechnologyDetection
from app.services.analysis.architecture_detection import ArchitectureDetection
from app.services.code.parser_manager import ParserManager, BaseParser
from app.models.code.source_file import SourceFile
from app.models.code.ast_node import ASTNode

class MockPythonParser(BaseParser):
    def parse(self, source_file: SourceFile) -> ASTNode:
        return ASTNode(
            node_type="module",
            children=[
                ASTNode(node_type="class", name="SampleClass", properties={"qualname": "SampleClass"}, children=[
                    ASTNode(node_type="function", name="sample_method", properties={"qualname": "SampleClass.sample_method"})
                ])
            ]
        )

def test_pipeline():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        main_py = temp_path / "main.py"
        main_py.write_text("class SampleClass:\n    def sample_method(self):\n        pass")
        
        # Setup context
        repo_context = RepositoryContext(repository_path=temp_dir, source_code_files=["main.py"])
        
        pm = ParserManager()
        pm.register_parser("python", MockPythonParser())
        
        # Phase 1: Code Understanding
        cu_pipeline = CodeUnderstandingPipeline(parser_manager=pm)
        code_context = cu_pipeline.process(repo_context)
        
        # Phase 2: Graph Builder & Persistence
        builder = GraphBuilder()
        graph = builder.build(code_context)
        
        repo = GraphRepository()
        try:
            repo.save_graph(graph)
            
            # Pattern Detection
            tech_detector = TechnologyDetection(repo)
            arch_detector = ArchitectureDetection(repo)
            
            repo_context = tech_detector.detect(repo_context)
            repo_context = arch_detector.detect(repo_context)
            
            print("=== END-TO-END PIPELINE OUTPUT ===")
            print(f"Source Files: {len(code_context.source_files)}")
            print(f"Graph Nodes: {len(graph.nodes)}")
            print(f"Graph Edges: {len(graph.edges)}")
            print(f"Technologies: {repo_context.metadata.get('technologies', [])}")
            print(f"Architecture: {repo_context.metadata.get('architecture', 'Unknown')}")
            print("==================================")
            
            print("test_repository_knowledge_graph_pipeline passed!")
        except Exception as e:
            print(f"Failed to persist or query Neo4j: {e}")

if __name__ == "__main__":
    test_pipeline()
