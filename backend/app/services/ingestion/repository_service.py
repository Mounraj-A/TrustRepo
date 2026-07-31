from pathlib import Path
import shutil
import re

from git import Repo, GitCommandError


class RepositoryService:
    """
    Repository Ingestion Service

    Layer 1 – Repository Ingestion & Preprocessing

    Responsibilities
    ----------------
    - Validate GitHub repository URLs
    - Clone repositories
    - Detect existing repositories
    - Extract repository metadata
    - Delete local repositories
    """

    def __init__(self):
        self.repositories_dir = Path("repositories")
        self.repositories_dir.mkdir(exist_ok=True)

    # ---------------------------------------------------------
    # URL VALIDATION
    # ---------------------------------------------------------

    def validate_repository_url(self, url: str) -> bool:
        pattern = (
            r"^https://github\.com/"
            r"[A-Za-z0-9_.-]+/"
            r"[A-Za-z0-9_.-]+/?$"
        )

        return re.match(pattern, url) is not None

    # ---------------------------------------------------------
    # LOCAL REPOSITORY CHECK
    # ---------------------------------------------------------

    def repository_exists(self, repository_name: str) -> bool:
        return (self.repositories_dir / repository_name).exists()

    # ---------------------------------------------------------
    # CLONE REPOSITORY
    # ---------------------------------------------------------

    def clone_repository(self, url: str) -> dict:

        if not self.validate_repository_url(url):
            raise ValueError("Invalid GitHub repository URL.")

        repository_name = url.rstrip("/").split("/")[-1]

        destination = self.repositories_dir / repository_name

        if destination.exists():
            return {
                "status": "already_exists",
                "repository_name": repository_name,
                "local_path": str(destination.resolve()),
            }

        try:
            Repo.clone_from(url, destination)

            return {
                "status": "cloned",
                "repository_name": repository_name,
                "local_path": str(destination.resolve()),
            }

        except GitCommandError as error:
            raise RuntimeError(f"Repository clone failed:\n{error}")

    # ---------------------------------------------------------
    # REPOSITORY METADATA
    # ---------------------------------------------------------

    def get_repository_metadata(self, repository_path: str | Path) -> dict:
        """
        Extract metadata from a cloned repository.

        Parameters
        ----------
        repository_path : str | Path
            Absolute or relative path to the cloned repository.
        """

        repository_path = Path(repository_path)

        if not repository_path.exists():
            raise FileNotFoundError(
                f"Repository not found: {repository_path}"
            )

        repo = Repo(repository_path)

        return {
            "repository_name": repository_path.name,
            "repository_path": str(repository_path.resolve()),
            "default_branch": repo.active_branch.name,
            "latest_commit": repo.head.commit.hexsha,
            "latest_commit_message": repo.head.commit.message.strip(),
        }

    # ---------------------------------------------------------
    # DELETE REPOSITORY
    # ---------------------------------------------------------

    def delete_repository(self, repository_name: str) -> bool:

        repository_path = self.repositories_dir / repository_name

        if not repository_path.exists():
            return False

        shutil.rmtree(repository_path)

        return True