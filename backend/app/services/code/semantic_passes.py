"""
Semantic Passes for AST Nodes

These passes run after initial AST parsing to extract deeper semantic
information: call graphs, inheritance edges, and type annotations.
Each pass receives the ASTNode tree and enriches it with additional
child nodes representing discovered relationships.

Every node added by a semantic pass becomes a Knowledge Graph node,
ensuring all evidence is traceable to parser output.
"""
import ast as pyast
from typing import Optional
from app.models.code.ast_node import ASTNode
from app.models.code.source_file import SourceFile


class CallGraphPass:
    """
    Extracts method-level call relationships from Python ASTs.
    Adds Call nodes as children of Method/Function nodes.

    Output: ASTNode(node_type="Call", name="<callee>", ...)
    """

    def run(self, root: ASTNode, source_file: SourceFile) -> ASTNode:
        """Enrich root with Call nodes from the source file."""
        content = source_file.content or ""
        try:
            tree = pyast.parse(content)
        except SyntaxError:
            return root

        # Map function name -> ASTNode for enrichment
        func_nodes: dict[str, ASTNode] = {}
        for child in root.children:
            if child.node_type in ("Function", "Method"):
                func_nodes[child.name] = child
            elif child.node_type == "Class":
                for m in child.children:
                    if m.node_type in ("Function", "Method"):
                        func_nodes[f"{child.name}.{m.name}"] = m

        # Walk AST to find call sites inside each function
        for node in pyast.walk(tree):
            if isinstance(node, (pyast.FunctionDef, pyast.AsyncFunctionDef)):
                callee_name = node.name
                target_node = func_nodes.get(callee_name)
                if target_node is None:
                    continue
                for child_node in pyast.walk(node):
                    if isinstance(child_node, pyast.Call):
                        callee = self._get_call_name(child_node.func)
                        if callee:
                            target_node.children.append(ASTNode(
                                node_type="Call",
                                name=callee,
                                start_line=getattr(child_node, "lineno", None),
                            ))
        return root

    def _get_call_name(self, node) -> Optional[str]:
        if isinstance(node, pyast.Name):
            return node.id
        elif isinstance(node, pyast.Attribute):
            obj = self._get_call_name(node.value)
            if obj:
                return f"{obj}.{node.attr}"
            return node.attr
        return None


class InheritancePass:
    """
    Extracts class inheritance relationships.
    Adds Inherits nodes as children of Class nodes.

    Output: ASTNode(node_type="Inherits", name="<base_class>", ...)
    """

    def run(self, root: ASTNode, source_file: SourceFile) -> ASTNode:
        content = source_file.content or ""
        try:
            tree = pyast.parse(content)
        except SyntaxError:
            return root

        class_nodes = {
            child.name: child for child in root.children if child.node_type == "Class"}

        for node in pyast.walk(tree):
            if isinstance(node, pyast.ClassDef):
                class_node = class_nodes.get(node.name)
                if class_node is None:
                    continue
                for base in node.bases:
                    base_name = self._get_name(base)
                    if base_name:
                        class_node.children.append(ASTNode(
                            node_type="Inherits",
                            name=base_name,
                            start_line=getattr(node, "lineno", None),
                        ))
        return root

    def _get_name(self, node) -> Optional[str]:
        if isinstance(node, pyast.Name):
            return node.id
        elif isinstance(node, pyast.Attribute):
            obj = self._get_name(node.value)
            return f"{obj}.{node.attr}" if obj else node.attr
        return None


class TypeResolutionPass:
    """
    Extracts type annotations from function signatures and variable assignments.
    Adds TypeAnnotation nodes as children of Method/Function/Variable nodes.

    Output: ASTNode(node_type="TypeAnnotation", name="<type>", ...)
    """

    def run(self, root: ASTNode, source_file: SourceFile) -> ASTNode:
        content = source_file.content or ""
        try:
            tree = pyast.parse(content)
        except SyntaxError:
            return root

        func_nodes: dict[str, ASTNode] = {}
        for child in root.children:
            if child.node_type in ("Function", "Method"):
                func_nodes[child.name] = child
            elif child.node_type == "Class":
                for m in child.children:
                    if m.node_type in ("Function", "Method"):
                        func_nodes[f"{child.name}.{m.name}"] = m

        for node in pyast.walk(tree):
            if isinstance(node, (pyast.FunctionDef, pyast.AsyncFunctionDef)):
                fn_node = func_nodes.get(node.name)
                if fn_node is None:
                    continue
                # Return type annotation
                if node.returns:
                    ret_type = pyast.unparse(node.returns)
                    fn_node.children.append(ASTNode(
                        node_type="TypeAnnotation",
                        name=f"returns:{ret_type}",
                        start_line=getattr(node, "lineno", None),
                    ))
                # Parameter type annotations
                for arg in node.args.args:
                    if arg.annotation:
                        param_type = pyast.unparse(arg.annotation)
                        fn_node.children.append(ASTNode(
                            node_type="TypeAnnotation",
                            name=f"param:{arg.arg}:{param_type}",
                            start_line=getattr(node, "lineno", None),
                        ))
        return root


class SemanticPassRunner:
    """
    Runs all semantic passes in order on a parsed ASTNode tree.
    Only runs Python-aware passes for Python source files.
    Language-specific passes are skipped for other file types.
    """

    def __init__(self):
        self.python_passes = [
            CallGraphPass(),
            InheritancePass(),
            TypeResolutionPass(),
        ]

    def run(self, root: ASTNode, source_file: SourceFile) -> ASTNode:
        lang = (source_file.language or "").lower()
        if lang == "python":
            for pass_ in self.python_passes:
                try:
                    root = pass_.run(root, source_file)
                except Exception:
                    pass  # Individual pass failures must not break pipeline
        return root
