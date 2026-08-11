from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class ASTNode:
    """
    Language-independent AST Node representation.
    """
    node_type: str
    name: Optional[str] = None
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    children: List['ASTNode'] = field(default_factory=list)
