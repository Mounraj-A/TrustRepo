from app.models.claim import Claim
from app.models.claim_type import ClaimType
from app.models.verification_status import VerificationStatus


def main():

    claim = Claim(
        id="claim_001",
        text="Backend uses Spring Boot.",
        source_document="README.md",
        source_section="Technology Stack",
        claim_type=ClaimType.TECHNOLOGY,
        confidence=0.95,
    )

    print("=" * 60)
    print("CLAIM MODEL TEST")
    print("=" * 60)

    print("ID:", claim.id)
    print("Text:", claim.text)
    print("Type:", claim.claim_type.value)
    print("Status:", claim.verification_status.value)
    print("Confidence:", claim.confidence)
    print("Source:", claim.source_document)
    print("Section:", claim.source_section)


if __name__ == "__main__":
    main()