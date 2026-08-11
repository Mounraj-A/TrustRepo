from enum import Enum


class ClaimType(str, Enum):
    """
    Types of claims extracted from repository documentation.
    """

    TECHNOLOGY = "technology"
    FEATURE = "feature"
    CONFIGURATION = "configuration"
    API = "api"
    DATABASE = "database"
    DEPENDENCY = "dependency"
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    PERFORMANCE = "performance"
    DEPLOYMENT = "deployment"
    RUNTIME = "runtime"
    TESTING = "testing"
    UNKNOWN = "unknown"
