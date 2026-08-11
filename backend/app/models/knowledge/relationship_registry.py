from enum import Enum
from typing import List


class RelationshipType(str, Enum):
    # Structural
    CONTAINS = "CONTAINS"
    DECLARES = "DECLARES"

    # Code Dependencies
    IMPORTS = "IMPORTS"
    CALLS = "CALLS"
    USES = "USES"
    IMPLEMENTS = "IMPLEMENTS"
    DEPENDS_ON = "DEPENDS_ON"
    EXTENDS = "EXTENDS"

    # Semantic
    HAS_FEATURE = "HAS_FEATURE"
    HAS_CAPABILITY = "HAS_CAPABILITY"
    HAS_ARCHITECTURE = "HAS_ARCHITECTURE"
    USES_TECHNOLOGY = "USES_TECHNOLOGY"

    # Evidence
    SUPPORTED_BY = "SUPPORTED_BY"
    CONTRADICTS = "CONTRADICTS"


class RelationshipRegistry:
    """Central registry for all knowledge graph edge types."""

    @classmethod
    def all_types(cls) -> List[str]:
        return [r.value for r in RelationshipType]

    @classmethod
    def structural_types(cls) -> List[str]:
        return [
            RelationshipType.CONTAINS.value,
            RelationshipType.DECLARES.value
        ]

    @classmethod
    def semantic_types(cls) -> List[str]:
        return [
            RelationshipType.HAS_FEATURE.value,
            RelationshipType.HAS_CAPABILITY.value,
            RelationshipType.HAS_ARCHITECTURE.value,
            RelationshipType.USES_TECHNOLOGY.value
        ]
