import re
from app.models.code.source_file import SourceFile
from app.models.code.ast_node import ASTNode
from app.services.code.parsers.base_parser import BaseParser


class JavaScriptParser(BaseParser):
    def parse(self, source_file: SourceFile) -> ASTNode:
        root = ASTNode(node_type="File", name=source_file.path)
        content = source_file.content or ""

        # Classes
        class_pattern = re.compile(r'class\s+([A-Za-z0-9_]+)')
        for match in class_pattern.finditer(content):
            root.children.append(ASTNode(
                node_type="Class",
                name=match.group(1),
                start_line=content[:match.start()].count('\n') + 1,
                properties={"content": match.group(0)}
            ))

        # Decorators / Annotations
        annotation_pattern = re.compile(r'@([A-Za-z0-9_]+)')
        for match in annotation_pattern.finditer(content):
            root.children.append(ASTNode(
                node_type="Annotation",
                name=match.group(1),
                start_line=content[:match.start()].count('\n') + 1,
                properties={"content": match.group(0)}
            ))

        # Imports
        import_pattern = re.compile(
            r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]')
        for match in import_pattern.finditer(content):
            root.children.append(ASTNode(
                node_type="Import",
                name=match.group(1),
                start_line=content[:match.start()].count('\n') + 1,
                properties={"content": match.group(0)}
            ))

        return root
