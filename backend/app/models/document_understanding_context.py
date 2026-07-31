from dataclasses import dataclass, field
from typing import Dict, List

from app.models.claim import Claim
from app.models.document_context import Document
from app.models.document_section import DocumentSection
from app.models.processed_document import ProcessedDocument


@dataclass
class DocumentUnderstandingContext:
    """
    Stores every intermediate artifact produced by the
    Document Understanding pipeline.
    """

    documents: List[Document] = field(default_factory=list)

    processed_documents: List[ProcessedDocument] = field(default_factory=list)

    sections: List[DocumentSection] = field(default_factory=list)

    candidate_claims: List[Claim] = field(default_factory=list)

    metadata: Dict = field(default_factory=dict)