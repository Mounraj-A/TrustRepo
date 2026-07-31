from app.models.repository_context import RepositoryContext
from app.services.ingestion.context_builder import RepositoryContextBuilder
from app.services.ingestion.repository_normalizer import RepositoryNormalizer
from app.services.ingestion.repository_scanner import RepositoryScanner
from app.services.ingestion.repository_service import RepositoryService


class RepositoryIngestionPipeline:
    """
    Layer 1 – Repository Ingestion & Preprocessing

    This pipeline orchestrates the complete repository ingestion
    workflow and produces a RepositoryContext object for the
    downstream TrustRepo layers.
    """

    def __init__(self):
        self.repository_service = RepositoryService()
        self.repository_scanner = RepositoryScanner()
        self.repository_normalizer = RepositoryNormalizer()
        self.context_builder = RepositoryContextBuilder()

    def ingest(self, repository_url: str) -> RepositoryContext:
        """
        Execute the complete repository ingestion pipeline.

        Parameters
        ----------
        repository_url : str
            GitHub repository URL.

        Returns
        -------
        RepositoryContext
            Fully prepared repository context.
        """

        # ---------------------------------------------------------
        # Step 1 - Clone Repository
        # ---------------------------------------------------------
        clone_result = self.repository_service.clone_repository(repository_url)

        if clone_result["status"] not in ("cloned", "already_exists"):
            raise Exception(
                f"Repository cloning failed: {clone_result.get('message', 'Unknown error')}"
            )

        repository_path = clone_result["local_path"]

        # ---------------------------------------------------------
        # Step 2 - Extract Repository Metadata
        # ---------------------------------------------------------
        metadata = self.repository_service.get_repository_metadata(
            repository_path
        )

        # ---------------------------------------------------------
        # Step 3 - Scan Repository
        # ---------------------------------------------------------
        scan_results = self.repository_scanner.scan_repository(
            repository_path
        )

        # ---------------------------------------------------------
        # Step 4 - Normalize Repository
        # ---------------------------------------------------------
        normalized_results = self.repository_normalizer.normalize(
            scan_results
        )

        # ---------------------------------------------------------
        # Step 5 - Build Repository Context
        # ---------------------------------------------------------
        context = self.context_builder.build(
            repository_url=repository_url,
            repository_path=repository_path,
            metadata=metadata,
            normalized_results=normalized_results,
        )

        return context