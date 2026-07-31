import re

from app.models.document_context import DocumentContext


class ClaimNormalizer:
    """
    Normalizes candidate claims.

    This stage enriches the existing Claim objects instead of
    creating separate NormalizedClaim objects.
    """

    def normalize(
        self,
        document_context: DocumentContext,
    ) -> DocumentContext:

        document_context.normalized_claims = []

        for claim in document_context.candidate_claims:

            normalized = claim.text

            normalized = normalized.lower()

            normalized = re.sub(r"\*\*", "", normalized)

            normalized = re.sub(r"`", "", normalized)

            normalized = re.sub(r"\s+", " ", normalized)

            normalized = normalized.strip()

            claim.normalized_text = normalized

            claim.metadata["normalized"] = True

            document_context.normalized_claims.append(claim)

        document_context.metadata["normalized_claims"] = len(
            document_context.normalized_claims
        )

        return document_context