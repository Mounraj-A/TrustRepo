from app.models.document_context import DocumentContext
from app.models.repository_context import RepositoryContext

from app.services.analysis.document_collector import (
    DocumentCollector,
)
from app.services.analysis.document_preprocessor import (
    DocumentPreprocessor,
)
from app.services.analysis.document_segmenter import (
    DocumentSegmenter,
)
from app.services.analysis.statement_extractor import (
    StatementExtractor,
)
from app.services.analysis.claim_candidate_generator import (
    ClaimCandidateGenerator,
)
from app.services.analysis.claim_normalizer import (
    ClaimNormalizer,
)
from app.services.analysis.claim_deduplicator import (
    ClaimDeduplicator,
)
from app.services.analysis.claim_repository_builder import (
    ClaimRepositoryBuilder,
)


class DocumentUnderstandingPipeline:
    """
    Executes the complete Document Understanding pipeline.
    """

    def __init__(self):

        self.collector = DocumentCollector()

        self.preprocessor = DocumentPreprocessor()

        self.segmenter = DocumentSegmenter()

        self.statement_extractor = StatementExtractor()

        self.claim_generator = ClaimCandidateGenerator()

        self.claim_normalizer = ClaimNormalizer()

        self.claim_deduplicator = ClaimDeduplicator()

        self.claim_repository_builder = (
            ClaimRepositoryBuilder()
        )

    def process(
        self,
        repository_context: RepositoryContext,
    ) -> DocumentContext:

        # Stage 1
        document_context = self.collector.collect(repository_context)
        print("Documents              :", len(document_context.documents))

        # Stage 2
        document_context = self.preprocessor.preprocess(document_context)
        print("Processed Documents    :", len(document_context.processed_documents))

        # Stage 3
        document_context = self.segmenter.segment(document_context)
        print("Sections               :", len(document_context.sections))

        # Stage 4
        document_context = self.statement_extractor.extract(document_context)
        print("Atomic Statements      :", len(document_context.atomic_statements))

        # Stage 5
        document_context = self.claim_generator.generate(document_context)
        print("Candidate Claims       :", len(document_context.candidate_claims))

        # Stage 6
        document_context = self.claim_normalizer.normalize(document_context)
        print("Normalized Claims      :", len(document_context.normalized_claims))

        # Stage 7
        document_context = self.claim_deduplicator.deduplicate(document_context)
        print("Deduplicated Claims    :", len(document_context.deduplicated_claims))

        # Stage 8
        document_context = self.claim_repository_builder.build(document_context)
        print("Repository Claims      :", len(document_context.claim_repository))

        # ==========================================================
        # Pipeline Statistics
        # ==========================================================

        document_context.metadata.update(
            {
                "documents": len(
                    document_context.documents
                ),
                "processed_documents": len(
                    document_context.processed_documents
                ),
                "sections": len(
                    document_context.sections
                ),
                "atomic_statements": len(
                    document_context.atomic_statements
                ),
                "candidate_claims": len(
                    document_context.candidate_claims
                ),
                "normalized_claims": len(
                    document_context.normalized_claims
                ),
                "deduplicated_claims": len(
                    document_context.deduplicated_claims
                ),
                "claim_repository": len(
                    document_context.claim_repository
                ),
            }
        )

        return document_context