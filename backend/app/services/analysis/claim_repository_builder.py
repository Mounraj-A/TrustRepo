from app.models.claim_repository import ClaimRepository
from app.models.document_context import DocumentContext


class ClaimRepositoryBuilder:
    """
    Builds the final repository of documentation claims.

    The Claim Repository is the output of the
    Document Understanding pipeline and the input
    to the Claim–Evidence Matching Engine.
    """

    def build(
        self,
        document_context: DocumentContext,
    ) -> DocumentContext:

        repository = ClaimRepository()

        repository.extend(
            document_context.deduplicated_claims
        )

        document_context.claim_repository = repository

        return document_context
