from app.models.code.code_context import CodeContext
from app.models.code.intermediate_representation import IntermediateRepresentation, IRNode
from app.models.code.relationship import Relationship

class RelationshipExtractor:
    """
    Extracts relationships (CONTAINS, DEFINES, ANNOTATED_WITH, IMPORTS)
    from UIR nodes to build the full Knowledge Graph edge schema.
    """
    def extract(self, code_context: CodeContext) -> CodeContext:
        if code_context.intermediate_representation is None:
            return code_context
            
        for ir in code_context.intermediate_representation:
            self._extract_from_ir(ir, code_context)
        return code_context

    def _extract_from_ir(self, ir: IntermediateRepresentation, context: CodeContext):
        for node in ir.nodes:
            self._visit(node, ir.file_path, context)

    def _visit(self, node: IRNode, file_path: str, context: CodeContext):
        for child in node.children:
            rel_type = self._infer_relationship(node.type, child.type)
            
            if node.qualname and child.qualname:
                rel = Relationship(
                    source_qualname=node.qualname,
                    target_qualname=child.qualname,
                    type=rel_type,
                    properties={"file_path": file_path}
                )
                context.relationships.append(rel)
            self._visit(child, file_path, context)

    def _infer_relationship(self, parent_type: str, child_type: str) -> str:
        """
        Map (parent_type, child_type) → relationship type following the
        full Knowledge Graph schema.
        """
        parent_lower = (parent_type or "").lower()
        child_lower = (child_type or "").lower()

        if child_lower == "annotation":
            return "ANNOTATED_WITH"
        elif child_lower == "import":
            return "IMPORTS"
        elif child_lower in ("method", "function", "constructor"):
            return "DEFINES"
        elif child_lower == "class":
            return "CONTAINS"
        elif child_lower == "interface":
            return "CONTAINS"
        elif child_lower == "variable":
            return "HAS_FIELD"
        else:
            return "CONTAINS"

