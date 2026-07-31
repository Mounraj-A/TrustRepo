from pathlib import Path


class RepositoryScanner:
    """
    Repository Scanner

    Layer 1 - Repository Ingestion & Preprocessing

    Responsibilities
    ----------------
    - Scan repository contents
    - Discover important files
    - Classify repository files
    """

    DOCUMENTATION_FILES = {
        "README.md",
        "README.rst",
        "README.txt",
        "CONTRIBUTING.md",
        "CHANGELOG.md",
        "LICENSE",
        "LICENSE.md",
    }

    CONFIGURATION_FILES = {
        "requirements.txt",
        "package.json",
        "pyproject.toml",
        "Dockerfile",
        "docker-compose.yml",
        ".gitignore",
        ".env.example",
    }

    SOURCE_CODE_EXTENSIONS = {
        ".py",
        ".js",
        ".ts",
        ".java",
        ".cpp",
        ".c",
        ".cs",
        ".go",
        ".rs",
    }

    TEST_KEYWORDS = {
        "test",
        "tests",
    }

    def scan_repository(self, repository_path: str) -> dict:
        """
        Scan the repository and classify files.
        """

        repository = Path(repository_path)

        if not repository.exists():
            raise FileNotFoundError("Repository does not exist.")

        results = {
            "documentation": [],
            "source_code": [],
            "tests": [],
            "configuration": [],
            "ci_cd": [],
            "other": [],
        }

        for file in repository.rglob("*"):

            if not file.is_file():
                continue

            relative_path = str(file.relative_to(repository))
            filename = file.name

            # Documentation
            if filename in self.DOCUMENTATION_FILES:
                results["documentation"].append(relative_path)
                continue

            # Configuration
            if filename in self.CONFIGURATION_FILES:
                results["configuration"].append(relative_path)
                continue

            # GitHub Actions
            if ".github/workflows" in relative_path.replace("\\", "/"):
                results["ci_cd"].append(relative_path)
                continue

            # Tests
            if any(keyword in relative_path.lower() for keyword in self.TEST_KEYWORDS):
                results["tests"].append(relative_path)
                continue

            # Source Code
            if file.suffix in self.SOURCE_CODE_EXTENSIONS:
                results["source_code"].append(relative_path)
                continue

            # Other
            results["other"].append(relative_path)

        return results