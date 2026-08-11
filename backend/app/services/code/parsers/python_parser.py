import ast
from app.models.code.source_file import SourceFile
from app.models.code.ast_node import ASTNode
from app.services.code.parsers.base_parser import BaseParser


class PythonParser(BaseParser):
    def parse(self, source_file: SourceFile) -> ASTNode:
        root = ASTNode(node_type="File", name=source_file.path)
        content = source_file.content or ""

        try:
            tree = ast.parse(content)
        except Exception:
            return root

        def visit(node, parent_ast):
            if isinstance(node, ast.ClassDef):
                class_node = ASTNode(
                    node_type="Class",
                    name=node.name,
                    start_line=getattr(node, 'lineno', None),
                    end_line=getattr(node, 'end_lineno', None),
                )
                # Decorators (Annotations)
                for dec in node.decorator_list:
                    dec_name = self._get_name(dec)
                    if dec_name:
                        class_node.children.append(ASTNode(
                            node_type="Annotation",
                            name=dec_name,
                            start_line=getattr(dec, 'lineno', None)
                        ))
                parent_ast.children.append(class_node)
                for child in ast.iter_child_nodes(node):
                    visit(child, class_node)

            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                func_node = ASTNode(
                    node_type="Method" if parent_ast.node_type == "Class" else "Function",
                    name=node.name,
                    start_line=getattr(node, 'lineno', None),
                    end_line=getattr(node, 'end_lineno', None),
                )
                for dec in node.decorator_list:
                    dec_name = self._get_name(dec)
                    if dec_name:
                        func_node.children.append(ASTNode(
                            node_type="Annotation",
                            name=dec_name,
                            start_line=getattr(dec, 'lineno', None)
                        ))
                parent_ast.children.append(func_node)
                # We can skip going deep into function bodies to save graph size, or we can go deep.
                # For TrustRepo, we just want methods, not statements inside.

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    props = {}
                    if alias.asname:
                        props["alias"] = alias.asname
                    parent_ast.children.append(ASTNode(
                        node_type="Import",
                        name=alias.name,
                        start_line=getattr(node, 'lineno', None),
                        properties=props
                    ))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    full_name = f"{module}.{
                        alias.name}" if module else alias.name
                    props = {}
                    if alias.asname:
                        props["alias"] = alias.asname
                    parent_ast.children.append(ASTNode(
                        node_type="Import",
                        name=full_name,
                        start_line=getattr(node, 'lineno', None),
                        properties=props
                    ))
            else:
                for child in ast.iter_child_nodes(node):
                    visit(child, parent_ast)

        for child in ast.iter_child_nodes(tree):
            visit(child, root)

        return root

    def _get_name(self, node):
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Call):
            return self._get_name(node.func)
        return None
