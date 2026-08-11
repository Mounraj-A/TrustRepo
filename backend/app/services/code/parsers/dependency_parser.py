import json
import re
from pathlib import Path

from app.models.code.source_file import SourceFile
from app.models.code.ast_node import ASTNode
from app.services.code.parsers.base_parser import BaseParser


class DependencyParser(BaseParser):
    """
    Parses dependency configuration files natively to extract explicit dependencies.
    Supports: requirements.txt, package.json
    """

    def parse(self, source_file: SourceFile) -> ASTNode:
        root = ASTNode(node_type="File", name=source_file.path)
        content = source_file.content or ""
        filename = Path(source_file.path).name.lower()

        if filename == "package.json":
            self._parse_package_json(content, root)
        elif filename == "requirements.txt":
            self._parse_requirements(content, root)
        elif filename == "pyproject.toml" or filename.endswith(".toml"):
            self._parse_toml_dependencies(content, root)
        # Extend to pom.xml (xml.etree), build.gradle, etc. as needed

        return root

    def _parse_package_json(self, content: str, root: ASTNode):
        try:
            data = json.loads(content)
            deps = data.get("dependencies", {})
            dev_deps = data.get("devDependencies", {})

            for dep, version in {**deps, **dev_deps}.items():
                root.children.append(ASTNode(
                    node_type="Dependency",
                    name=dep,
                    start_line=1,
                    properties={"version": version}
                ))
        except Exception:
            pass

    def _parse_requirements(self, content: str, root: ASTNode):
        lines = content.splitlines()
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Parse name and version separately (e.g. numpy==1.24.0,
            # flask>=2.0)
            match = re.match(r"^([a-zA-Z0-9_\-\.]+)([>=<!]+([0-9\.]+))?", line)
            if match:
                dep_name = match.group(1)
                dep_version = match.group(3) or ""
                root.children.append(ASTNode(
                    node_type="Dependency",
                    name=dep_name,
                    start_line=i + 1,
                    properties={"version": dep_version}
                ))

    def _parse_toml_dependencies(self, content: str, root: ASTNode):
        """
        Since tomllib is 3.11+ and this project targets 3.10+,
        we use basic string parsing as a fallback.
        In a real scenario, `pip install tomli` would be used.
        """
        lines = content.splitlines()
        in_deps = False
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith("[") and line.endswith("]"):
                in_deps = "dependencies" in line.lower()
                continue

            if in_deps and line and not line.startswith("#"):
                if "=" in line:
                    dep_name = line.split("=")[0].strip().strip('"').strip("'")
                    if dep_name:
                        root.children.append(ASTNode(
                            node_type="Dependency",
                            name=dep_name,
                            start_line=i + 1
                        ))
