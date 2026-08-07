from app.services.ingestion.repository_ingestion_pipeline import (
    RepositoryIngestionPipeline,
)


def main():
    repository_url = "https://github.com/Mounraj-A/College_Event_Management"

    pipeline = RepositoryIngestionPipeline()

    context = pipeline.ingest(repository_url)

    print("=" * 60)
    print("Repository Context")
    print("=" * 60)

    print(f"Repository Name : {context.repository_name}")
    print(f"Repository URL  : {context.repository_url}")
    print(f"Repository Path : {context.repository_path}")

    print()

    print("Metadata")
    print("-" * 60)

    for key, value in context.metadata.items():
        print(f"{key}: {value}")

    print()

    print(f"Documentation Files : {len(context.documentation_files)}")
    print(f"Source Code Files   : {len(context.source_code_files)}")
    print(f"Test Files          : {len(context.test_files)}")
    print(f"Configuration Files : {len(context.configuration_files)}")
    print(f"CI/CD Files         : {len(context.ci_cd_files)}")
    print(f"Other Files         : {len(context.other_files)}")


if __name__ == "__main__":
    main()