from app.models.repository_context import RepositoryContext


class RepositoryContextBuilder:
    """
    Repository Context Builder — Layer 1

    Combines repository metadata and normalized scan results into a
    single RepositoryContext object consumed by Layer 2 and beyond.
    Every scanner category maps to a typed field on RepositoryContext.
    """

    def build(
        self,
        repository_url: str,
        repository_path: str,
        metadata: dict,
        normalized_results: dict,
    ) -> RepositoryContext:

        context = RepositoryContext()

        # ── Repository Information ─────────────────────────────────────────
        context.repository_url = repository_url
        context.repository_path = repository_path
        context.repository_name = metadata.get("repository_name", "")

        # ── Repository Metadata (git metadata, branch, commit hash…) ──────
        context.metadata = metadata

        # ── Evidence Categories ────────────────────────────────────────────
        context.source_code_files          = normalized_results.get("source_code", [])
        context.test_files                 = normalized_results.get("tests", [])
        context.documentation_files        = normalized_results.get("documentation", [])
        context.build_files                = normalized_results.get("build_files", [])
        context.package_manifests          = normalized_results.get("package_manifests", [])
        context.infrastructure_files       = normalized_results.get("infrastructure", [])
        context.ci_cd_files                = normalized_results.get("ci_cd", [])
        context.infrastructure_as_code_files = normalized_results.get("infrastructure_as_code", [])
        context.configuration_files        = normalized_results.get("configuration", [])
        context.script_files               = normalized_results.get("scripts", [])
        context.generated_files            = normalized_results.get("generated", [])
        context.asset_files                = normalized_results.get("assets", [])
        context.other_files                = normalized_results.get("other", [])

        return context