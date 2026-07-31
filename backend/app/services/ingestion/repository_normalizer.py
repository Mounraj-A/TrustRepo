from pathlib import Path


class RepositoryNormalizer:
    """
    Repository Normalization Engine

    Layer 1 – Repository Ingestion & Preprocessing

    Responsibilities
    ----------------
    - Remove unwanted directories
    - Ignore generated files
    - Keep only useful evidence files
    """

    EXCLUDED_DIRECTORIES = {
        ".git",
        ".github",
        "node_modules",
        "build",
        "dist",
        "target",
        "__pycache__",
        ".venv",
        ".idea",
        ".vscode",
        ".pytest_cache",
    }

    EXCLUDED_EXTENSIONS = {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".ico",
        ".pdf",
        ".zip",
        ".jar",
        ".class",
        ".exe",
        ".dll",
        ".so",
        ".pyc",
        ".log",
        ".lock",
        ".map",
    }

    def normalize(self, scan_results: dict) -> dict:
        """
        Normalize repository scan results by removing
        generated files and unnecessary directories.

        Parameters
        ----------
        scan_results : dict
            Output from RepositoryScanner.

        Returns
        -------
        dict
            Cleaned repository contents.
        """

        normalized_results = {}

        for category, files in scan_results.items():

            cleaned_files = []

            for file in files:

                path = Path(file)

                # Skip excluded directories
                if any(part in self.EXCLUDED_DIRECTORIES for part in path.parts):
                    continue

                # Skip excluded file extensions
                if path.suffix.lower() in self.EXCLUDED_EXTENSIONS:
                    continue

                cleaned_files.append(str(path))

            normalized_results[category] = sorted(cleaned_files)

        return normalized_results