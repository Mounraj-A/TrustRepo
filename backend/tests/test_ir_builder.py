from app.models.code.source_file import SourceFile
from app.models.code.ast_node import ASTNode
from app.services.code.builders.ir_builder import IRBuilder

def test_ir_builder():
    ast_root = ASTNode(
        node_type="module",
        children=[
            ASTNode(node_type="class", name="MyClass", children=[
                ASTNode(node_type="function", name="my_method")
            ])
        ]
    )
    
    src = SourceFile(path="test.py", language="python", content="", extension=".py", size=0)
    builder = IRBuilder()
    ir = builder.build(src, ast_root)
    
    assert len(ir.nodes) == 1
    assert ir.nodes[0].type == "class"
    assert ir.nodes[0].name == "MyClass"
    assert len(ir.nodes[0].children) == 1
    assert ir.nodes[0].children[0].type == "function"
    assert ir.nodes[0].children[0].name == "my_method"
    
    print("test_ir_builder passed!")

if __name__ == "__main__":
    test_ir_builder()
