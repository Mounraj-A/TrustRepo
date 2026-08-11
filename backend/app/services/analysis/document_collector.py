from pathlib import Path

from app.models.document_context import Document, DocumentContext
from app.models.repository_context import RepositoryContext


class DocumentCollector:
    """
    Collect all repository documentation.

    Input:
        RepositoryContext

    Output:
        DocumentContext
    """

    README_NAMES = {
        "README.md",
        "README.txt",
        "README.rst",
    }

    CHANGELOG_NAMES = {
        "CHANGELOG.md",
        "CHANGES.md",
        "HISTORY.md",
    }

    def collect(self, context: RepositoryContext) -> DocumentContext:

        document_context = DocumentContext()

        for file in context.documentation_files:

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

            document = Document(
                path=file,
                document_type=self._detect_document_type(file),
                content=content,
            )

            document_context.documents.append(document)

            name = Path(file).name.upper()

            if name.startswith("README"):
                document_context.readme_files.append(document)

            elif name.startswith("CHANGELOG") or name.startswith("HISTORY"):
                document_context.changelog_files.append(document)

            elif file.lower().endswith(".md"):
                document_context.markdown_files.append(document)

        return document_context

    def _detect_document_type(self, file: str) -> str:

        name = Path(file).name.lower()

        if name.startswith("readme"):
            return "README"

        if name.startswith("changelog"):
            return "CHANGELOG"

        if name.startswith("history"):
            return "HISTORY"

        if file.endswith(".md"):
            return "MARKDOWN"

        return "DOCUMENT"
