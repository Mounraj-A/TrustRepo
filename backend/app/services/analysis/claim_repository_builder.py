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

        repository.metadata = {
            "total_claims": len(repository),
            "claim_types": len(
                {
                    claim.claim_type.value
                    for claim in repository.claims
                }
            ),
        }

        document_context.claim_repository = repository

        document_context.metadata[
            "claim_repository"
        ] = len(repository)

        return document_context