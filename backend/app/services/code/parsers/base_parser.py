from app.models.code.source_file import SourceFile
from app.models.code.ast_node import ASTNode
from typing import Optional


class BaseParser:
    def parse(self, source_file: SourceFile) -> Optional[ASTNode]:
        raise NotImplementedError()
