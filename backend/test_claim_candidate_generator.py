from app.services.ingestion.repository_ingestion_pipeline import RepositoryIngestionPipeline
from app.services.analysis.document_collector import DocumentCollector
from app.services.analysis.document_preprocessor import DocumentPreprocessor
from app.services.analysis.document_segmenter import DocumentSegmenter
from app.services.analysis.claim_candidate_generator import ClaimCandidateGenerator


def main():

    repository_url = "https://github.com/Mounraj-A/College_Event_Management"

    pipeline = RepositoryIngestionPipeline()

    context = pipeline.ingest(repository_url)

    collector = DocumentCollector()
    documents = collector.collect(context)

    preprocessor = DocumentPreprocessor()
    processed_documents = preprocessor.preprocess(documents)

    segmenter = DocumentSegmenter()
    sections = segmenter.segment(processed_documents)

    generator = ClaimCandidateGenerator()
    claims = generator.generate(sections)

    print("=" * 70)
    print("CLAIM CANDIDATES")
    print("=" * 70)

    print(f"Total Claims: {len(claims)}")

    for index, claim in enumerate(claims, start=1):

        print()
        print(f"[{index}]")
        print("Type      :", claim.claim_type.value)
        print("Section   :", claim.source_section)
        print("Confidence:", claim.confidence)
        print("Text      :", claim.text)


if __name__ == "__main__":
    main()