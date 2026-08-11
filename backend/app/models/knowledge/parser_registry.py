from enum import Enum


class ParserReliability(float, Enum):
    """
    Standardized reliability scores for different parsing engines.
    Used by the Confidence Engine to weigh evidence.
    """
    TREE_SITTER = 1.00
    JAVALANG = 0.95
    ESPRIMA = 0.95
    BABEL = 0.95
    REGEX = 0.40
    HEURISTIC = 0.30


class ParserRegistry:
    """Central registry for AST and source code parsers."""

    @classmethod
    def get_reliability(cls, parser_name: str) -> float:
        mapping = {
            "tree-sitter": ParserReliability.TREE_SITTER,
            "javalang": ParserReliability.JAVALANG,
            "esprima": ParserReliability.ESPRIMA,
            "babel": ParserReliability.BABEL,
            "regex": ParserReliability.REGEX,
            "heuristic": ParserReliability.HEURISTIC
        }
        return mapping.get(parser_name.lower(), 0.50)
