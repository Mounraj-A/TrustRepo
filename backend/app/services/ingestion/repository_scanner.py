from pathlib import Path
from typing import Dict, List


class RepositoryScanner:
    """
    Repository Scanner — Layer 1

    Discovers and classifies every file in a repository into
    semantically meaningful categories. Every category produces
    evidence for downstream pipeline layers.

    Categories
    ----------
    documentation     : README, CONTRIBUTING, CHANGELOG, docs/**
    source_code       : .py .js .ts .java .go .rs .cpp .cs etc.
    tests             : test/** spec/** *_test.* *.test.* *.spec.*
    configuration     : .env application.yml settings.py *.ini *.cfg
    build_files       : pom.xml build.gradle Cargo.toml go.mod etc.
    package_manifests : requirements.txt package.json Pipfile etc.
    infrastructure    : Dockerfile docker-compose.yml compose.yaml
    ci_cd             : .github/workflows/ Jenkinsfile .travis.yml
    infrastructure_as_code : terraform helm kubernetes
    scripts           : *.sh *.bash *.ps1 scripts/**
    generated         : migrations/ generated/
    assets            : images, fonts, static files
    other             : everything else
    """

    # ── Documentation ────────────────────────────────────────────────────────
    DOCUMENTATION_NAMES = {
        "README.md", "README.rst", "README.txt", "README",
        "CONTRIBUTING.md", "CONTRIBUTING.rst",
        "CHANGELOG.md", "CHANGELOG.rst", "CHANGELOG.txt",
        "LICENSE", "LICENSE.md", "LICENSE.txt",
        "CODE_OF_CONDUCT.md", "SECURITY.md",
        "ARCHITECTURE.md", "DESIGN.md",
    }
    DOCUMENTATION_DIRS = {"docs", "doc", "documentation", "wiki"}

    # ── Source Code ──────────────────────────────────────────────────────────
    SOURCE_EXTENSIONS = {
        ".py", ".js", ".jsx", ".ts", ".tsx",
        ".java", ".kt", ".scala",
        ".go", ".rs", ".c", ".cpp", ".cc", ".h", ".hpp",
        ".cs", ".fs", ".vb",
        ".rb", ".php", ".swift", ".dart", ".lua",
        ".r", ".m", ".jl",
    }

    # ── Build Files ──────────────────────────────────────────────────────────
    BUILD_FILE_NAMES = {
        "pom.xml", "build.gradle", "build.gradle.kts",
        "settings.gradle", "settings.gradle.kts",
        "Cargo.toml", "Cargo.lock",
        "go.mod", "go.sum",
        "Gemfile", "Gemfile.lock",
        "composer.json", "composer.lock",
        "Makefile", "GNUmakefile", "makefile",
        "CMakeLists.txt", "meson.build", "build.bazel",
        "BUCK", "BUILD",
    }

    # ── Package Manifests ────────────────────────────────────────────────────
    PACKAGE_MANIFEST_NAMES = {
        "requirements.txt", "requirements-dev.txt", "requirements-test.txt",
        "Pipfile", "Pipfile.lock",
        "pyproject.toml", "setup.py", "setup.cfg",
        "poetry.lock", "environment.yml", "conda.yml",
        "package.json", "package-lock.json",
        "yarn.lock", "pnpm-lock.yaml", ".npmrc",
        "Gemfile", "Gemfile.lock",
        "composer.json",
    }

    # ── Infrastructure (Docker/Compose) ──────────────────────────────────────
    INFRASTRUCTURE_NAMES = {
        "Dockerfile", "Containerfile",
        "docker-compose.yml", "docker-compose.yaml",
        "docker-compose.dev.yml", "docker-compose.prod.yml",
        "docker-compose.test.yml",
        "compose.yml", "compose.yaml",
        ".dockerignore",
    }
    INFRASTRUCTURE_EXTENSIONS = {".dockerfile"}

    # ── CI/CD ─────────────────────────────────────────────────────────────────
    CICD_NAMES = {
        "Jenkinsfile", ".travis.yml", ".travis.yaml",
        "appveyor.yml", "appveyor.yaml",
        "azure-pipelines.yml", "azure-pipelines.yaml",
        "bitbucket-pipelines.yml",
        ".drone.yml", ".drone.yaml",
        "Fastfile",
    }
    CICD_DIRS = {
        ".github/workflows",
        ".circleci",
        ".gitlab-ci",
        ".buildkite",
        ".azure",
    }

    # ── Infrastructure as Code ────────────────────────────────────────────────
    IAC_EXTENSIONS = {".tf", ".tfvars"}
    IAC_DIRS = {"terraform", "helm", "charts", "k8s", "kubernetes", "infra", "infrastructure", "deploy", "deployment"}
    IAC_NAMES = {"Chart.yaml", "values.yaml", "kustomization.yaml", "kustomization.yml"}

    # ── Configuration ─────────────────────────────────────────────────────────
    CONFIG_NAMES = {
        ".env", ".env.example", ".env.sample", ".env.local",
        "config.json", "config.yaml", "config.yml",
        "application.yml", "application.yaml",
        "application.properties",
        "settings.py", "settings.json",
        ".eslintrc", ".eslintrc.json", ".eslintrc.js",
        ".prettierrc", ".babelrc",
        "tsconfig.json", "jsconfig.json",
        "webpack.config.js", "vite.config.ts", "vite.config.js",
        "next.config.js", "nuxt.config.js",
        ".gitignore", ".gitattributes",
        "nginx.conf", "apache.conf",
    }
    CONFIG_EXTENSIONS = {".ini", ".cfg", ".conf", ".toml", ".properties"}

    # ── Scripts ──────────────────────────────────────────────────────────────
    SCRIPT_EXTENSIONS = {".sh", ".bash", ".zsh", ".fish", ".ps1", ".bat", ".cmd"}
    SCRIPT_DIRS = {"scripts", "bin", "tools"}

    # ── Generated ────────────────────────────────────────────────────────────
    GENERATED_DIRS = {"migrations", "migration", "generated", "__generated__", "dist", "build", ".next", "out"}

    # ── Assets ───────────────────────────────────────────────────────────────
    ASSET_EXTENSIONS = {
        ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp",
        ".ttf", ".woff", ".woff2", ".eot",
        ".mp4", ".webm", ".ogg", ".mp3",
        ".pdf", ".docx",
    }

    # ── Exclude ──────────────────────────────────────────────────────────────
    EXCLUDE_DIRS = {
        "__pycache__", ".git", ".svn", ".hg",
        "node_modules", ".venv", "venv", "env",
        ".tox", ".pytest_cache", ".mypy_cache",
        ".gradle", ".mvn",
        "target",  # Java Maven
    }

    def scan_repository(self, repository_path: str) -> Dict[str, List[str]]:
        """
        Scan the repository and classify every file into evidence categories.

        Returns
        -------
        dict with keys: documentation, source_code, tests, build_files,
        package_manifests, infrastructure, ci_cd, infrastructure_as_code,
        configuration, scripts, generated, assets, other
        """
        root = Path(repository_path)
        if not root.exists():
            raise FileNotFoundError(f"Repository path does not exist: {repository_path}")

        results: Dict[str, List[str]] = {
            "documentation": [],
            "source_code": [],
            "tests": [],
            "build_files": [],
            "package_manifests": [],
            "infrastructure": [],
            "ci_cd": [],
            "infrastructure_as_code": [],
            "configuration": [],
            "scripts": [],
            "generated": [],
            "assets": [],
            "other": [],
        }

        for file in root.rglob("*"):
            if not file.is_file():
                continue

            # Build relative path with forward slashes for consistency
            try:
                rel = file.relative_to(root)
            except ValueError:
                continue

            rel_str = str(rel).replace("\\", "/")
            rel_parts = [p.lower() for p in rel.parts]
            filename = file.name
            suffix = file.suffix.lower()

            # ── Skip excluded dirs ────────────────────────────────────────
            if any(part in self.EXCLUDE_DIRS for part in rel_parts[:-1]):
                continue

            # ── 1. Generated (check before source code) ───────────────────
            if any(part in self.GENERATED_DIRS for part in rel_parts[:-1]):
                results["generated"].append(rel_str)
                continue

            # ── 2. CI/CD ──────────────────────────────────────────────────
            if filename in self.CICD_NAMES:
                results["ci_cd"].append(rel_str)
                continue
            if any(cicd_dir in rel_str for cicd_dir in self.CICD_DIRS):
                results["ci_cd"].append(rel_str)
                continue

            # ── 3. Infrastructure as Code ─────────────────────────────────
            if suffix in self.IAC_EXTENSIONS:
                results["infrastructure_as_code"].append(rel_str)
                continue
            if filename in self.IAC_NAMES:
                results["infrastructure_as_code"].append(rel_str)
                continue
            if any(part in self.IAC_DIRS for part in rel_parts[:-1]):
                if suffix in {".yaml", ".yml", ".json"}:
                    results["infrastructure_as_code"].append(rel_str)
                    continue

            # ── 4. Infrastructure (Docker) ────────────────────────────────
            if filename in self.INFRASTRUCTURE_NAMES or suffix in self.INFRASTRUCTURE_EXTENSIONS:
                results["infrastructure"].append(rel_str)
                continue

            # ── 5. Build Files ────────────────────────────────────────────
            if filename in self.BUILD_FILE_NAMES:
                results["build_files"].append(rel_str)
                continue

            # ── 6. Package Manifests ──────────────────────────────────────
            if filename in self.PACKAGE_MANIFEST_NAMES:
                results["package_manifests"].append(rel_str)
                continue

            # ── 7. Documentation ──────────────────────────────────────────
            if filename in self.DOCUMENTATION_NAMES:
                results["documentation"].append(rel_str)
                continue
            if any(part in self.DOCUMENTATION_DIRS for part in rel_parts[:-1]):
                if suffix in {".md", ".rst", ".txt", ".html"}:
                    results["documentation"].append(rel_str)
                    continue

            # ── 8. Scripts ────────────────────────────────────────────────
            if suffix in self.SCRIPT_EXTENSIONS:
                results["scripts"].append(rel_str)
                continue
            if any(part in self.SCRIPT_DIRS for part in rel_parts[:-1]):
                results["scripts"].append(rel_str)
                continue

            # ── 9. Configuration ──────────────────────────────────────────
            if filename in self.CONFIG_NAMES or suffix in self.CONFIG_EXTENSIONS:
                results["configuration"].append(rel_str)
                continue

            # ── 10. Assets ────────────────────────────────────────────────
            if suffix in self.ASSET_EXTENSIONS:
                results["assets"].append(rel_str)
                continue

            # ── 11. Tests ─────────────────────────────────────────────────
            is_test = (
                "test" in rel_parts[:-1] or "tests" in rel_parts[:-1] or
                "spec" in rel_parts[:-1] or "specs" in rel_parts[:-1] or
                filename.startswith("test_") or filename.endswith("_test.py") or
                ".test." in filename or ".spec." in filename
            )
            if is_test and suffix in self.SOURCE_EXTENSIONS:
                results["tests"].append(rel_str)
                continue

            # ── 12. Source Code ───────────────────────────────────────────
            if suffix in self.SOURCE_EXTENSIONS:
                results["source_code"].append(rel_str)
                continue

            # ── 13. Other ─────────────────────────────────────────────────
            results["other"].append(rel_str)

        return results