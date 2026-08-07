from pathlib import Path

from app.models.code.code_context import CodeContext
from app.models.code.source_file import SourceFile
from app.models.repository_context import RepositoryContext


class SourceFileCollector:
    """
    Collect all repository source code files.

    Input:
        RepositoryContext

    Output:
        CodeContext
    """

    def collect(self, context: RepositoryContext) -> CodeContext:

        code_context = CodeContext()

        for file in context.source_code_files:

            path = Path(context.repository_path) / file

            if not path.exists():
                continue

            try:
                content = path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
            except Exception:
                content = ""

            source_file = SourceFile(
                path=file,
                language="",
                content=content,
                extension=path.suffix,
                size=path.stat().st_size,
            )

            code_context.source_files.append(source_file)

        return code_context
