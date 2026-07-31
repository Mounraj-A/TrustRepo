import re

from app.models.document_context import DocumentContext
from app.models.document_section import DocumentSection


class DocumentSegmenter:
    """
    Splits processed documents into semantic sections.

    This stage enriches the DocumentContext by populating
    its sections collection.
    """

    def segment(
        self,
        document_context: DocumentContext,
    ) -> DocumentContext:

        document_context.sections = []

        heading_pattern = re.compile(r"^(#{1,6})\s+(.*)$")

        for document in document_context.processed_documents:

            current_title = "Introduction"
            current_level = 1
            current_content = []

            for line in document.original_content.splitlines():

                match = heading_pattern.match(line)

                if match:

                    if current_content:

                        document_context.sections.append(
                            DocumentSection(
                                document_path=document.path,
                                document_type=document.document_type,
                                title=current_title,
                                content="\n".join(current_content).strip(),
                                level=current_level,
                            )
                        )

                    current_level = len(match.group(1))
                    current_title = match.group(2).strip()
                    current_content = []

                else:

                    current_content.append(line)

            if current_content:

                document_context.sections.append(
                    DocumentSection(
                        document_path=document.path,
                        document_type=document.document_type,
                        title=current_title,
                        content="\n".join(current_content).strip(),
                        level=current_level,
                    )
                )

        document_context.metadata["sections"] = len(
            document_context.sections
        )

        return document_context