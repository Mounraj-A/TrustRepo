from app.models.repository_context import RepositoryContext
from app.models.code.code_context import CodeContext
from app.services.code.source_file_collector import SourceFileCollector
from app.services.code.language_detector import LanguageDetector
from app.services.code.parser_manager import ParserManager
from app.services.code.builders.ir_builder import IRBuilder
from app.services.knowledge.symbol_extractor import SymbolExtractor
from app.services.knowledge.relationship_extractor import RelationshipExtractor

class CodeUnderstandingPipeline:
    """
    Orchestrates the Code Understanding pipeline (Layer 2B).
    Enriches a single CodeContext object at each stage.
    """
    def __init__(self, parser_manager: ParserManager = None, source_collector: SourceFileCollector = None):
        self.collector = source_collector or SourceFileCollector()
        self.language_detector = LanguageDetector()
        self.parser_manager = parser_manager or ParserManager()
        self.ir_builder = IRBuilder()
        self.symbol_extractor = SymbolExtractor()
        self.relationship_extractor = RelationshipExtractor()

    def process(self, repository_context: RepositoryContext) -> CodeContext:
        # Stage 1: Collect Source Files
        code_context = self.collector.collect(repository_context)
        print("Source Files           :", len(code_context.source_files))

        # Stage 2: Language Detection
        code_context = self.language_detector.detect(code_context)
        print("Detected Languages     :", len(code_context.detected_languages))

        # Stage 3: Parsing
        if code_context.parsed_files is None:
            code_context.parsed_files = []
        if code_context.ast_nodes is None:
            code_context.ast_nodes = []
        if code_context.intermediate_representation is None:
            code_context.intermediate_representation = []
            
        for source_file in code_context.source_files:
            ast = self.parser_manager.parse(source_file)
            if ast:
                code_context.parsed_files.append(source_file.path)
                code_context.ast_nodes.append(ast)
                
                # Stage 4: IR Building
                ir = self.ir_builder.build(source_file, ast)
                code_context.intermediate_representation.append(ir)

        print("Parsed ASTs            :", len(code_context.ast_nodes))
        print("UIRs Built             :", len(code_context.intermediate_representation))

        # Stage 5: Symbol Extraction
        code_context = self.symbol_extractor.extract(code_context)
        print("Extracted Symbols      :", len(code_context.symbols))

        # Stage 6: Relationship Extraction
        code_context = self.relationship_extractor.extract(code_context)
        print("Extracted Relationships:", len(code_context.relationships))

        return code_context
