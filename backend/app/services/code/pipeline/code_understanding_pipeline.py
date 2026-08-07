from app.models.repository_context import RepositoryContext
from app.models.code.code_context import CodeContext
from app.models.code.source_file import SourceFile
from app.services.code.source_file_collector import SourceFileCollector
from app.services.code.language_detector import LanguageDetector
from app.services.code.parser_manager import ParserManager
from app.services.code.parsers.dependency_parser import DependencyParser
from app.services.code.builders.ir_builder import IRBuilder
from app.services.code.semantic_passes import SemanticPassRunner
from app.services.knowledge.symbol_extractor import SymbolExtractor
from app.services.knowledge.relationship_extractor import RelationshipExtractor
import os


class CodeUnderstandingPipeline:
    """
    Orchestrates the Code Understanding pipeline (Layer 2B).

    Stages
    ------
    1. Source File Collection
    2. Language Detection
    3. AST Parsing (per-language)
    4. Semantic Passes (Call Graph, Inheritance, Type Resolution)
    5. IR Building (UIR)
    6. Dependency Parsing (build files + package manifests)
    7. Symbol Extraction
    8. Relationship Extraction
    """

    def __init__(
        self,
        parser_manager: ParserManager = None,
        source_collector: SourceFileCollector = None,
    ):
        self.collector = source_collector or SourceFileCollector()
        self.language_detector = LanguageDetector()
        self.parser_manager = parser_manager or ParserManager()
        self.dependency_parser = DependencyParser()
        self.ir_builder = IRBuilder()
        self.semantic_passes = SemanticPassRunner()
        self.symbol_extractor = SymbolExtractor()
        self.relationship_extractor = RelationshipExtractor()

    def process(self, repository_context: RepositoryContext) -> CodeContext:
        # ── Stage 1: Collect Source Files ─────────────────────────────────
        code_context = self.collector.collect(repository_context)
        print("Source Files           :", len(code_context.source_files))

        # ── Stage 2: Language Detection ───────────────────────────────────
        code_context = self.language_detector.detect(code_context)
        print("Detected Languages     :", len(code_context.detected_languages))

        # ── Stage 3 & 4: Parsing + Semantic Passes ────────────────────────
        if code_context.parsed_files is None:
            code_context.parsed_files = []
        if code_context.ast_nodes is None:
            code_context.ast_nodes = []
        if code_context.intermediate_representation is None:
            code_context.intermediate_representation = []

        for source_file in code_context.source_files:
            ast_root = self.parser_manager.parse(source_file)
            if ast_root:
                # Semantic passes enrich the AST with Call, Inherits, TypeAnnotation nodes
                ast_root = self.semantic_passes.run(ast_root, source_file)
                code_context.parsed_files.append(source_file.path)
                code_context.ast_nodes.append(ast_root)

                # ── Stage 5: IR Building ───────────────────────────────────
                ir = self.ir_builder.build(source_file, ast_root)
                code_context.intermediate_representation.append(ir)

        print("Parsed ASTs            :", len(code_context.ast_nodes))
        print("UIRs Built             :", len(code_context.intermediate_representation))

        # ── Stage 6: Dependency Parsing ────────────────────────────────────
        # Parse build files and package manifests to extract Dependency nodes
        dep_files = (
            (repository_context.build_files or []) +
            (repository_context.package_manifests or [])
        )
        repo_path = repository_context.repository_path or ""
        dep_ast_count = 0
        for rel_path in dep_files:
            full_path = os.path.join(repo_path, rel_path)
            if not os.path.exists(full_path):
                continue
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                dep_source = SourceFile(
                    path=rel_path,
                    language="dependency",
                    content=content,
                )
                dep_ast = self.dependency_parser.parse(dep_source)
                if dep_ast and dep_ast.children:
                    code_context.ast_nodes.append(dep_ast)
                    dep_ast_count += 1
            except Exception:
                pass

        print("Dependency ASTs        :", dep_ast_count)

        # ── Stage 7: Symbol Extraction ────────────────────────────────────
        code_context = self.symbol_extractor.extract(code_context)
        print("Extracted Symbols      :", len(code_context.symbols))

        # ── Stage 8: Relationship Extraction ──────────────────────────────
        code_context = self.relationship_extractor.extract(code_context)
        print("Extracted Relationships:", len(code_context.relationships))

        return code_context
