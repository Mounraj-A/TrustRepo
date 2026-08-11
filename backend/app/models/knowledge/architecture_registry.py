from enum import Enum
from typing import List


class ArchitecturePattern(str, Enum):
    MICROSERVICES = "Microservices"
    MONOLITH = "Monolith"
    EVENT_DRIVEN = "Event-Driven"
    SERVERLESS = "Serverless"
    CQRS = "CQRS"
    MVC = "MVC"
    LAYERED = "Layered Architecture"
    PLUGIN = "Plugin Architecture"


class ArchitectureRegistry:
    """Central registry for architectural patterns."""

    @classmethod
    def all_patterns(cls) -> List[str]:
        return [p.value for p in ArchitecturePattern]
