from pathlib import Path
from app.models.code.code_context import CodeContext

class LanguageDetector:
    """
    Detects the programming language of source files based on extension or heuristics.
    """
    EXTENSION_MAP = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".java": "java",
        ".go": "go",
        ".cs": "csharp",
        ".cpp": "cpp",
        ".c": "c",
        ".h": "c",
        ".hpp": "cpp",
        ".rb": "ruby",
        ".php": "php"
    }

    def detect(self, code_context: CodeContext) -> CodeContext:
        for source_file in code_context.source_files:
            path_obj = Path(source_file.path)
            ext = path_obj.suffix.lower()
            name = path_obj.name.lower()
            
            if name in ["package.json", "requirements.txt", "pyproject.toml", "poetry.lock", "cargo.toml", "pom.xml", "pipfile", "pipfile.lock", "build.gradle"]:
                source_file.language = "dependency"
            else:
                source_file.language = self.EXTENSION_MAP.get(ext, "unknown")
            
            if source_file.language not in code_context.detected_languages:
                code_context.detected_languages[source_file.language] = 0
            code_context.detected_languages[source_file.language] += 1
            
        return code_context
