from dataclasses import dataclass, field
from typing import Any, Dict, List

from app.models.code.source_file import SourceFile


@dataclass
class CodeContext:
    """
    Central context object for the Code Understanding pipeline.

    Every stage enriches this object instead of creating
    new collections independently.
    """

    # ==========================================================
    # Stage 1 : Source File Collection
    # ==========================================================

    source_files: List[SourceFile] = field(default_factory=list)

    # ==========================================================
    # Stage 2 : Language Detection
    # ==========================================================

    detected_languages: Dict[str, int] = field(default_factory=dict)

    # ==========================================================
    # Stage 3 : Parsing
    # ==========================================================

    parsed_files: List[Any] = field(default_factory=list)

    ast_nodes: List[Any] = field(default_factory=list)

    # ==========================================================
    # Stage 4 : Symbol Extraction
    # ==========================================================

    symbols: List[Any] = field(default_factory=list)

    # ==========================================================
    # Stage 5 : Relationship Extraction
    # ==========================================================

    relationships: List[Any] = field(default_factory=list)

    # ==========================================================
    # Stage 6 : Intermediate Representation
    # ==========================================================

    intermediate_representation: Any = None