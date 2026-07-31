from app.services.analysis.document_collector import DocumentCollector
from app.services.analysis.document_preprocessor import DocumentPreprocessor
from app.services.analysis.document_segmenter import DocumentSegmenter
from app.services.ingestion.repository_ingestion_pipeline import (
    RepositoryIngestionPipeline,
)


def main():

    repo = "https://github.com/Mounraj-A/College_Event_Management"

    pipeline = RepositoryIngestionPipeline()

    context = pipeline.ingest(repo)

    collector = DocumentCollector()

    docs = collector.collect(context)

    preprocessor = DocumentPreprocessor()

    processed = preprocessor.preprocess(docs)

    segmenter = DocumentSegmenter()

    sections = segmenter.segment(processed)

    print("=" * 70)
    print("DOCUMENT SEGMENTS")
    print("=" * 70)

    print("Sections:", len(sections))

    print()

    for section in sections:

        print(section.title)

        print("-" * 40)

        print(section.content[:200])

        print()

        print("=" * 70)


if __name__ == "__main__":
    main()