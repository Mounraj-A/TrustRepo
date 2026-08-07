from app.services.ingestion.repository_ingestion_pipeline import (
    RepositoryIngestionPipeline,
)

from app.services.code.source_file_collector import (
    SourceFileCollector,
)


def main():

    repository_url = (
        "https://github.com/Mounraj-A/College_Event_Management"
    )

    ingestion = RepositoryIngestionPipeline()

    repository_context = ingestion.ingest(repository_url)

    collector = SourceFileCollector()

    code_context = collector.collect(repository_context)

    print("=" * 70)
    print("SOURCE FILE COLLECTOR")
    print("=" * 70)

    print()

    print("Total Source Files :", len(code_context.source_files))

    print()

    print("=" * 70)
    print("FIRST TEN FILES")
    print("=" * 70)

    for source_file in code_context.source_files[:10]:

        print()

        print("Path      :", source_file.path)
        print("Extension :", source_file.extension)
        print("Size      :", source_file.size)


if __name__ == "__main__":
    main()