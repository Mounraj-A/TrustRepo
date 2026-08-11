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

    def _extract_from_ir(self, ir: IntermediateRepresentation,
                         context: CodeContext):
        file_qualname = ir.file_path

        for node in ir.nodes:
            # Connect the top-level node to the file itself
            rel_type, confidence = self._infer_relationship("file", node.type)
            if node.qualname:
                rel = Relationship(
                    source_qualname=file_qualname,
                    target_qualname=node.qualname,
                    type=rel_type,
                    properties={"file_path": ir.file_path},
                    confidence=confidence
                )
                context.relationships.append(rel)

            self._visit(node, ir.file_path, context)

    def _visit(self, node: IRNode, file_path: str, context: CodeContext):
        for child in node.children:
            rel_type, confidence = self._infer_relationship(
                node.type, child.type)

            if node.qualname and child.qualname:
                rel = Relationship(
                    source_qualname=node.qualname,
                    target_qualname=child.qualname,
                    type=rel_type,
                    properties={"file_path": file_path},
                    confidence=confidence
                )
                context.relationships.append(rel)
            self._visit(child, file_path, context)

    def _infer_relationship(self, parent_type: str,
                            child_type: str) -> tuple[str, float]:
        """
        Map (parent_type, child_type) → (relationship_type, confidence) following the
        full Knowledge Graph schema.
        """
        parent_lower = (parent_type or "").lower()
        child_lower = (child_type or "").lower()

        if child_lower == "annotation" or child_lower == "decorator":
            return "ANNOTATED_WITH", 1.0
        elif child_lower == "import":
            return "IMPORTS", 1.0
        elif child_lower in ("method", "function", "constructor"):
            return "DECLARES", 1.0
        elif child_lower == "call":
            return "CALLS", 1.0
        elif child_lower == "identifier" and parent_lower in ("call", "method_invocation"):
            return "INVOKES", 0.9
        elif child_lower == "type" and parent_lower == "extends":
            return "EXTENDS", 1.0
        elif child_lower == "type" and parent_lower == "implements":
            return "IMPLEMENTS_INTERFACE", 1.0
        elif child_lower == "dependency":
            return "DEPENDS_ON", 1.0
        elif child_lower == "configuration":
            return "CONFIGURES", 1.0
        elif child_lower == "throw" or child_lower == "throws":
            return "THROWS", 1.0
        elif child_lower == "catch":
            return "CATCHES", 1.0
        elif child_lower == "variable":
            return "DECLARES", 1.0
        elif child_lower == "class" or child_lower == "interface":
            return "CONTAINS", 1.0
        elif parent_lower == "assignment" and child_lower == "identifier":
            return "WRITES", 0.9
        elif child_lower == "identifier":
            return "USES", 0.75
        elif child_lower == "return":
            return "RETURNS", 1.0
        elif child_lower == "new" or child_lower == "object_creation":
            return "CREATES", 1.0
        elif child_lower == "instanceof":
            return "INSTANCE_OF", 1.0
        else:
            return "CONTAINS", 0.5
