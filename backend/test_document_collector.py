from app.services.analysis.document_collector import DocumentCollector
from app.services.ingestion.repository_ingestion_pipeline import (
    RepositoryIngestionPipeline,
)


def main():

    repository_url = "https://github.com/Mounraj-A/College_Event_Management"

    pipeline = RepositoryIngestionPipeline()

    context = pipeline.ingest(repository_url)

    print("Repository:", context.repository_name)
    print("Documentation Files:", context.documentation_files)

    collector = DocumentCollector()

    document_context = collector.collect(context)

    print("=" * 60)
    print("DOCUMENT SUMMARY")
    print("=" * 60)

    print("Total:", len(document_context.documents))
    print("README:", len(document_context.readme_files))
    print("Markdown:", len(document_context.markdown_files))
    print("Changelog:", len(document_context.changelog_files))

    print()

    for document in document_context.documents:
        print(document.path)
        print(document.document_type)
        print(f"{len(document.content)} characters")
        print("-" * 40)


if __name__ == "__main__":
    main()