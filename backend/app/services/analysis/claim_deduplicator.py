from app.models.document_context import DocumentContext


class ClaimDeduplicator:
    """
    Removes duplicate normalized claims.

    Current implementation performs exact matching using
    claim type + normalized text.
    """

    def deduplicate(
        self,
        document_context: DocumentContext,
    ) -> DocumentContext:

        unique = set()

        document_context.deduplicated_claims = []

        for claim in document_context.normalized_claims:

            key = (
                claim.claim_type.value,
                claim.normalized_text.strip().lower(),
            )

            if key in unique:
                continue

            unique.add(key)

            document_context.deduplicated_claims.append(claim)

        document_context.metadata[
            "deduplicated_claims"
        ] = len(document_context.deduplicated_claims)

        return document_context