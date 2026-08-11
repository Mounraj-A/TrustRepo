import javalang
from app.models.code.source_file import SourceFile
from app.models.code.ast_node import ASTNode
from app.services.code.parsers.base_parser import BaseParser


class JavaParser(BaseParser):
    def parse(self, source_file: SourceFile) -> ASTNode:
        root = ASTNode(node_type="File", name=source_file.path)
        content = source_file.content or ""

        try:
            tree = javalang.parse.parse(content)
        except Exception:
            return root

        def _get_line(node):
            if hasattr(node, 'position') and node.position:
                return node.position.line
            return None

        for path, node in tree:
            if isinstance(node, javalang.tree.ClassDeclaration) or isinstance(
                    node, javalang.tree.InterfaceDeclaration):
                class_node = ASTNode(
                    node_type="Class" if isinstance(
                        node, javalang.tree.ClassDeclaration) else "Interface",
                    name=node.name,
                    start_line=_get_line(node)
                )

                # Annotations
                if node.annotations:
                    for ann in node.annotations:
                        class_node.children.append(ASTNode(
                            node_type="Annotation",
                            name=ann.name,
                            start_line=_get_line(ann)
                        ))

                # Methods
                for m in node.methods:
                    method_node = ASTNode(
                        node_type="Method",
                        name=m.name,
                        start_line=_get_line(m)
                    )
                    if m.annotations:
                        for ann in m.annotations:
                            method_node.children.append(ASTNode(
                                node_type="Annotation",
                                name=ann.name,
                                start_line=_get_line(ann)
                            ))
                    class_node.children.append(method_node)

                root.children.append(class_node)

            elif isinstance(node, javalang.tree.Import):
                root.children.append(ASTNode(
                    node_type="Import",
                    name=node.path,
                    start_line=_get_line(node)
                ))

        return root
