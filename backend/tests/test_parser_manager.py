from app.models.code.source_file import SourceFile
from app.models.code.ast_node import ASTNode
from app.services.code.parser_manager import ParserManager, BaseParser

class DummyPythonParser(BaseParser):
    def parse(self, source_file: SourceFile) -> ASTNode:
        return ASTNode(node_type="class", name="DummyClass")

def test_parser_manager():
    manager = ParserManager()
    manager.register_parser("python", DummyPythonParser())
    
    src = SourceFile(path="test.py", language="python", content="class DummyClass: pass", extension=".py", size=20)
    ast = manager.parse(src)
    
    assert ast is not None
    assert ast.node_type == "class"
    assert ast.name == "DummyClass"
    
    print("test_parser_manager passed!")

if __name__ == "__main__":
    test_parser_manager()
