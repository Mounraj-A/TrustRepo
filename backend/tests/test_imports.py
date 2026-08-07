def test_imports():

    import app.models.repository_context
    import app.models.document_context
    import app.models.processed_document
    import app.models.document_section

    import app.services.ingestion.repository_ingestion_pipeline
    import app.services.analysis.document_collector
    import app.services.analysis.document_preprocessor
    import app.services.analysis.document_segmenter

    print("===================================")
    print("All imports successful.")
    print("===================================")


if __name__ == "__main__":
    test_imports()