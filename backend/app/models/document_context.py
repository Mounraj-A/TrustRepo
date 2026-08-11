from dataclasses import dataclass, field
from typing import List

from app.models.atomic_statement import AtomicStatement
from app.models.claim import Claim
from app.models.claim_repository import ClaimRepository
from app.models.document_section import DocumentSection
from app.models.processed_document import ProcessedDocument


@dataclass
class Document:
    """
    Represents a single repository document.
    """

    path: str
    document_type: str
    content: str = ""


@dataclass
class DocumentContext:
    """
    Central context object for the complete Document Understanding
    pipeline.

    Each processing stage enriches this context instead of
    creating a new object.
    """

    # ==========================================================
    # Stage 1 : Document Collection
    # ==========================================================

    documents: List[Document] = field(default_factory=list)

    readme_files: List[Document] = field(default_factory=list)

    wiki_files: List[Document] = field(default_factory=list)

    markdown_files: List[Document] = field(default_factory=list)

    changelog_files: List[Document] = field(default_factory=list)

    api_documents: List[Document] = field(default_factory=list)

    issue_documents: List[Document] = field(default_factory=list)

    pull_request_documents: List[Document] = field(default_factory=list)

    # ==========================================================
    # Stage 2 : Document Preprocessing
    # ==========================================================

    processed_documents: List[ProcessedDocument] = field(default_factory=list)

    # ==========================================================
    # Stage 3 : Document Segmentation
    # ==========================================================

    sections: List[DocumentSection] = field(default_factory=list)

    # ==========================================================
    # Stage 4 : Atomic Statement Extraction
    # ==========================================================

    atomic_statements: List[AtomicStatement] = field(default_factory=list)

    # ==========================================================
    # Stage 5 : Candidate Claims
    # ==========================================================

    candidate_claims: List[Claim] = field(default_factory=list)

    # ==========================================================
    # Stage 6 : Normalized Claims
    # (Same Claim objects after normalization)
    # ==========================================================

    normalized_claims: List[Claim] = field(default_factory=list)

    # ==========================================================
    # Stage 7 : Deduplicated Claims
    # ==========================================================

    deduplicated_claims: List[Claim] = field(default_factory=list)

    # ==========================================================
    # Stage 8 : Claim Repository
    # ==========================================================

    claim_repository: ClaimRepository = field(
        default_factory=ClaimRepository
    )
