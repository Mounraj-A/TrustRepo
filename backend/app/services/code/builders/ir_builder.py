"""
IRBuilder — converts language-specific ASTs into the Unified Intermediate Representation (UIR).

Key fix: IRNode.qualname is now file-scoped to be globally unique:
    {file_path}::{parent_name}::{child_name}
This enables the RelationshipExtractor to correctly build edges.
"""
from typing import Optional
from app.models.code.ast_node import ASTNode
from app.models.code.intermediate_representation import IRNode, IntermediateRepresentation
from app.models.code.source_file import SourceFile


class IRBuilder:
    """
    Builds the Unified Intermediate Representation (UIR) from language-specific ASTs.
    Produces a properly qualified node tree so RelationshipExtractor can generate edges.
    """

    def build(self, source_file: SourceFile, ast_root: ASTNode) -> IntermediateRepresentation:
        ir = IntermediateRepresentation(
            file_path=source_file.path,
            language=source_file.language
        )
        if ast_root:
            for child in ast_root.children:
                node = self._visit(child, source_file.path, parent_qualname=source_file.path)
                if node:
                    ir.nodes.append(node)
        return ir

    def _visit(self, node: ASTNode, file_path: str, parent_qualname: str) -> Optional[IRNode]:
        ir_type = self._map_type(node.node_type)

        # Build a globally unique qualname scoped to the file
        safe_name = (node.name or "unknown").replace(" ", "_")
        qualname = f"{parent_qualname}::{safe_name}"

        ir_node = IRNode(
            type=ir_type,
            name=node.name or "unknown",
            qualname=qualname,
            file_path=file_path,
            start_line=node.start_line or 0,
            end_line=node.end_line or 0,
            metadata=node.properties.copy()
        )

        for child in node.children:
            child_node = self._visit(child, file_path, parent_qualname=qualname)
            if child_node:
                ir_node.children.append(child_node)

        return ir_node

    def _map_type(self, node_type: str) -> str:
        """Maps parser-specific node type strings to canonical UIR types."""
        nt = (node_type or "").lower()
        if "class" in nt:
            return "class"
        elif "interface" in nt:
            return "interface"
        elif "method" in nt:
            return "method"
        elif "function" in nt or "def" in nt:
            return "function"
        elif "annotation" in nt or "decorator" in nt:
            return "annotation"
        elif "import" in nt:
            return "import"
        elif "variable" in nt or "field" in nt:
            return "variable"
        else:
            return nt or "node"
