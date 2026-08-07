import re

from app.models.atomic_statement import AtomicStatement
from app.models.document_context import DocumentContext


class StatementExtractor:
    """
    Extracts atomic statements from semantic document sections.

    Each atomic statement should represent exactly one
    verifiable documentation statement.
    """

    def extract(
        self,
        document_context: DocumentContext,
    ) -> DocumentContext:

        document_context.atomic_statements = []

        for section in document_context.sections:

            statements = self._extract_statements(section.content)

            for index, statement in enumerate(statements):

                statement = statement.strip()

                if len(statement) < 10:
                    continue

                document_context.atomic_statements.append(
                    AtomicStatement(
                        document_path=section.document_path,
                        document_type=section.document_type,
                        section_title=section.title,
                        text=statement,
                        statement_index=index,
                    )
                )


        return document_context

    def _extract_statements(
        self,
        text: str,
    ) -> list[str]:
        """
        Split a section into atomic statements.

        Current heuristic:
        - Split by lines
        - Remove markdown bullets
        - Remove numbered bullets
        - Split into sentences
        """

        statements = []

        for line in text.splitlines():

            line = line.strip()

            if not line:
                continue

            # Remove markdown bullets
            line = re.sub(r"^[-*+]\s*", "", line)

            # Remove numbered bullets
            line = re.sub(r"^\d+\.\s*", "", line)

            parts = re.split(r"(?<=[.!?])\s+", line)

            for part in parts:

                part = part.strip()

                if part:
                    statements.append(part)

        return statements