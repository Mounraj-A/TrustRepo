import re

from app.models.document_context import DocumentContext
from app.models.processed_document import ProcessedDocument


class DocumentPreprocessor:
    """
    Cleans repository documentation before
    segmentation and claim extraction.

    This stage enriches the DocumentContext by populating
    its processed_documents collection.
    """

    def preprocess(
        self,
        document_context: DocumentContext,
    ) -> DocumentContext:

        document_context.processed_documents = []

        for document in document_context.documents:

            original = document.content

            headings = self._extract_headings(original)

            code_blocks = self._extract_code_blocks(original)

            cleaned = self._remove_code_blocks(original)

            cleaned = self._remove_markdown(cleaned)

            cleaned = self._normalize_whitespace(cleaned)

            document_context.processed_documents.append(
                ProcessedDocument(
                    path=document.path,
                    document_type=document.document_type,
                    original_content=original,
                    cleaned_content=cleaned,
                    headings=headings,
                    code_blocks=code_blocks,
                )
            )

        document_context.metadata["processed_documents"] = len(
            document_context.processed_documents
        )

        return document_context

    def _extract_headings(self, text: str) -> list[str]:

        headings = []

        for line in text.splitlines():

            line = line.strip()

            if line.startswith("#"):

                heading = line.lstrip("#").strip()

                if heading:
                    headings.append(heading)

        return headings

    def _extract_code_blocks(self, text: str) -> list[str]:

        return re.findall(
            r"```(.*?)```",
            text,
            flags=re.DOTALL,
        )

    def _remove_code_blocks(self, text: str) -> str:

        return re.sub(
            r"```.*?```",
            "",
            text,
            flags=re.DOTALL,
        )

    def _remove_markdown(self, text: str) -> str:

        text = re.sub(r"#+", "", text)

        text = re.sub(r"\*\*", "", text)

        text = re.sub(r"`", "", text)

        text = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1", text)

        text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)

        text = re.sub(r"^\-\s*", "", text, flags=re.MULTILINE)

        return text

    def _normalize_whitespace(self, text: str) -> str:

        lines = []

        for line in text.splitlines():

            line = line.strip()

            if line:
                lines.append(line)

        return "\n".join(lines)