from typing import Dict, Optional
from app.models.code.source_file import SourceFile
from app.models.code.ast_node import ASTNode

from app.services.code.parsers.base_parser import BaseParser
from app.services.code.parsers.java_parser import JavaParser
from app.services.code.parsers.python_parser import PythonParser
from app.services.code.parsers.javascript_parser import JavaScriptParser
from app.services.code.parsers.dependency_parser import DependencyParser


class ParserManager:
    """
    Registry for language-specific parsers.
    Uses Lightweight Language Parsers that yield common ASTNodes.
    """

    def __init__(self):
        self._parsers: Dict[str, BaseParser] = {
            "java": JavaParser(),
            "python": PythonParser(),
            "javascript": JavaScriptParser(),
            "typescript": JavaScriptParser(),
            "dependency": DependencyParser()
        }

    def register_parser(self, language: str, parser: BaseParser):
        self._parsers[language] = parser

    def get_parser(self, language: str) -> Optional[BaseParser]:
        return self._parsers.get(language.lower())

    def parse(self, source_file: SourceFile) -> Optional[ASTNode]:
        parser = self.get_parser(source_file.language)
        if parser:
            return parser.parse(source_file)
        return None
