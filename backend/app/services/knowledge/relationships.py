from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict
from uuid import uuid4


class RelationshipType(Enum):
    """
    Types of relationships between entities
    in the Repository Knowledge Graph.
    """

    CONTAINS = "CONTAINS"

    IMPORTS = "IMPORTS"

    CALLS = "CALLS"

    INHERITS = "INHERITS"

    IMPLEMENTS = "IMPLEMENTS"

    DOCUMENTS = "DOCUMENTS"

    TESTS = "TESTS"

    DEPENDS_ON = "DEPENDS_ON"

    REFERENCES = "REFERENCES"


@dataclass
class GraphRelationship:
    """
    Represents an edge in the Repository Knowledge Graph.
    """

    relationship_type: RelationshipType

    source_id: str

    target_id: str

    id: str = field(default_factory=lambda: str(uuid4()))

    attributes: Dict[str, Any] = field(default_factory=dict)