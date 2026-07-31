import inspect

from app.services.analysis.statement_extractor import StatementExtractor
from app.services.analysis.document_understanding_pipeline import (
    DocumentUnderstandingPipeline,
)
from app.services.ingestion.repository_ingestion_pipeline import (
    RepositoryIngestionPipeline,
)


def main():

    print("=" * 70)
    print("STATEMENT EXTRACTOR INFORMATION")
    print("=" * 70)

    print("Class :", StatementExtractor)
    print("Module:", StatementExtractor.__module__)
    print("File  :", inspect.getfile(StatementExtractor))

    print()

    repository_url = (
        "https://github.com/Mounraj-A/College_Event_Management"
    )

    ingestion = RepositoryIngestionPipeline()

    repository_context = ingestion.ingest(repository_url)

    pipeline = DocumentUnderstandingPipeline()

    document_context = pipeline.process(repository_context)

    print()
    print("=" * 70)
    print("DOCUMENT UNDERSTANDING PIPELINE")
    print("=" * 70)

    print()

    print("Documents           :", len(document_context.documents))
    print("Processed           :", len(document_context.processed_documents))
    print("Sections            :", len(document_context.sections))
    print("Atomic Statements   :", len(document_context.atomic_statements))
    print("Candidate Claims    :", len(document_context.candidate_claims))

    print()

    print("=" * 70)
    print("PIPELINE METADATA")
    print("=" * 70)

    for key, value in document_context.metadata.items():
        print(f"{key:20}: {value}")

    print()

    print("=" * 70)
    print("FIRST FIVE CLAIMS")
    print("=" * 70)

    if not document_context.candidate_claims:
        print("\nNo candidate claims generated.")
    else:
        for claim in document_context.candidate_claims[:5]:

            print()

            print("Type     :", claim.claim_type.value)
            print("Section  :", claim.source_section)
            print("Claim    :", claim.text)


if __name__ == "__main__":
    main()