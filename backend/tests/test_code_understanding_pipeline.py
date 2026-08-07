import os
import tempfile
from pathlib import Path
from app.models.repository_context import RepositoryContext
from app.services.code.pipeline.code_understanding_pipeline import CodeUnderstandingPipeline
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
        repo_context = RepositoryContext(
            repository_path=temp_dir,
            source_code_files=["main.py"]
        )
        
        # Setup Parser Manager
        pm = ParserManager()
        pm.register_parser("python", MockPythonParser())
        
        # Setup Pipeline
        pipeline = CodeUnderstandingPipeline(parser_manager=pm)
        
        # Run
        code_context = pipeline.process(repo_context)
        
        # Verifications
        assert code_context is not None
        assert "python" in code_context.detected_languages
        assert len(code_context.source_files) == 1
        assert len(code_context.parsed_files) == 1
        assert len(code_context.ast_nodes) == 1
        assert len(code_context.intermediate_representation) == 1
        assert len(code_context.symbols) == 2  # class and function
        assert len(code_context.relationships) == 1  # class defines function
        
        print("test_code_understanding_pipeline passed!")

if __name__ == "__main__":
    test_pipeline()
