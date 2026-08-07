import uuid

from app.models.claim import Claim
from app.models.claim_type import ClaimType
from app.models.document_context import DocumentContext


class ClaimCandidateGenerator:
    """
    Generates candidate claims from atomic statements using
    deterministic heuristic rules.

    This stage enriches the DocumentContext by populating
    its candidate_claims collection.
    """

    TECHNOLOGY_KEYWORDS = {
        "react",
        "spring",
        "spring boot",
        "java",
        "python",
        "mysql",
        "postgresql",
        "mongodb",
        "hibernate",
        "tailwind",
        "axios",
        "docker",
        "kubernetes",
    }

    FEATURE_KEYWORDS = {
        "allows",
        "allow",
        "supports",
        "support",
        "provides",
        "provide",
        "can",
        "create",
        "manage",
        "register",
        "login",
        "upload",
        "download",
    }

    CONFIGURATION_KEYWORDS = {
        "localhost",
        "port",
        "application.properties",
        "config",
        "configuration",
        ".env",
    }

    DATABASE_KEYWORDS = {
        "mysql",
        "postgresql",
        "mongodb",
        "database",
    }

    RUNTIME_KEYWORDS = {
        "run",
        "start",
        "server",
        "localhost",
        "port",
    }

    def generate(
        self,
        document_context: DocumentContext,
    ) -> DocumentContext:
        """
        Generate candidate claims from atomic statements.
        """

        document_context.candidate_claims = []

        for statement in document_context.atomic_statements:

            text = statement.text.strip()

            if len(text) < 15:
                continue

            claim_type = self._classify(text)

            if claim_type == ClaimType.UNKNOWN:
                continue

            claim = Claim(
                id=str(uuid.uuid4()),
                text=text,
                source_document=statement.document_path,
                source_section=statement.section_title,
                claim_type=claim_type,
                confidence=0.50
            )

            document_context.candidate_claims.append(claim)


        return document_context

    def _classify(
        self,
        text: str,
    ) -> ClaimType:
        """
        Classify a candidate claim using deterministic keyword rules.
        """

        text = text.lower()

        if any(keyword in text for keyword in self.TECHNOLOGY_KEYWORDS):
            return ClaimType.TECHNOLOGY

        if any(keyword in text for keyword in self.FEATURE_KEYWORDS):
            return ClaimType.FEATURE

        if any(keyword in text for keyword in self.CONFIGURATION_KEYWORDS):
            return ClaimType.CONFIGURATION

        if any(keyword in text for keyword in self.DATABASE_KEYWORDS):
            return ClaimType.DATABASE

        if any(keyword in text for keyword in self.RUNTIME_KEYWORDS):
            return ClaimType.RUNTIME

        return ClaimType.UNKNOWN