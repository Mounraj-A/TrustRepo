from app.models.code.code_context import CodeContext
from app.models.code.intermediate_representation import IntermediateRepresentation, IRNode
from app.models.code.symbol import Symbol


class SymbolExtractor:
    """
    Extracts symbols from UIR nodes.
    Uses the IRNode's own qualname (set by IRBuilder) to maintain
    consistency with RelationshipExtractor.
    """

    def extract(self, code_context: CodeContext) -> CodeContext:
        if code_context.intermediate_representation is None:
            code_context.intermediate_representation = []

        for ir in code_context.intermediate_representation:
            self._extract_from_ir(ir, code_context)
        return code_context

    def _extract_from_ir(self, ir: IntermediateRepresentation,
                         context: CodeContext):
        # Create a symbol for the file itself so top-level nodes can link to it
        file_sym = Symbol(
            name=ir.file_path.split(
                '/')[-1] if '/' in ir.file_path else ir.file_path.split('\\')[-1],
            qualname=ir.file_path,
            type="file",
            file_path=ir.file_path,
            start_line=1,
            properties={"language": ir.language}
        )
        context.symbols.append(file_sym)

        for node in ir.nodes:
            self._visit(node, ir.file_path, context)

    def _visit(self, node: IRNode, file_path: str, context: CodeContext):
        # IMPORTANT: use node.qualname as set by IRBuilder (file-scoped unique)
        # Do NOT regenerate qualname here — it would break
        # RelationshipExtractor
        sym = Symbol(
            name=node.name,
            qualname=node.qualname,   # Use IRNode's own qualname
            type=node.type,
            file_path=file_path,
            start_line=node.start_line,
            properties=node.metadata or {}
        )
        # node.qualname stays unchanged — both extractors now share the same
        # qualname
        context.symbols.append(sym)
        for child in node.children:
            self._visit(child, file_path, context)
