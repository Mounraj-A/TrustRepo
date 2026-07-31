from app.services.analysis.document_understanding_pipeline import (
    DocumentUnderstandingPipeline,
)
from app.services.ingestion.repository_ingestion_pipeline import (
    RepositoryIngestionPipeline,
)


def main():

    repository_url = (
        "https://github.com/Mounraj-A/College_Event_Management"
    )

    ingestion = RepositoryIngestionPipeline()

    repository_context = ingestion.ingest(
        repository_url
    )

    pipeline = DocumentUnderstandingPipeline()

    document_context = pipeline.process(
        repository_context
    )

    repository = document_context.claim_repository

    print("=" * 70)
    print("CLAIM REPOSITORY")
    print("=" * 70)

    print()

    print("Total Claims :", len(repository))

    print()

    print("Metadata")

    print("-" * 70)

    for key, value in repository.metadata.items():
        print(f"{key:20}: {value}")

    print()

    print("=" * 70)
    print("FIRST TEN CLAIMS")
    print("=" * 70)

    for claim in repository.claims[:10]:

        print()

        print("Type :", claim.claim_type.value)

        print("Normalized :", claim.normalized_text)

        print("Original :", claim.text)


if __name__ == "__main__":
    main()