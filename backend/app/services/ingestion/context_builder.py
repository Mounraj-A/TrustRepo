from app.models.repository_context import RepositoryContext


class RepositoryContextBuilder:
    """
    Repository Context Builder

    Layer 1 – Repository Ingestion & Preprocessing

    Combines repository metadata and normalized scan results into a
    single RepositoryContext object that will be consumed by Layer 2.
    """

    def build(
        self,
        repository_url: str,
        repository_path: str,
        metadata: dict,
        normalized_results: dict,
    ) -> RepositoryContext:

        context = RepositoryContext()

        # Repository Information
        context.repository_url = repository_url
        context.repository_path = repository_path
        context.repository_name = metadata.get("repository_name", "")

        # Repository Metadata

        # Normalized Repository Files
        context.documentation_files = normalized_results.get("documentation", [])
        context.source_code_files = normalized_results.get("source_code", [])
        context.test_files = normalized_results.get("tests", [])
        context.configuration_files = normalized_results.get("configuration", [])
        context.ci_cd_files = normalized_results.get("ci_cd", [])
        context.other_files = normalized_results.get("other", [])

        return context