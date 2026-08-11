from enum import Enum


class VerificationStatus(str, Enum):
    """
    Verification outcome for a documentation claim.
    """

    PENDING = "pending"

    SUPPORTED = "supported"

    PARTIALLY_SUPPORTED = "partially_supported"

    CONTRADICTED = "contradicted"

    UNSUPPORTED = "unsupported"

    UNKNOWN = "unknown"
