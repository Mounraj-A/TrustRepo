import pytest
from app.services.reporting.report_generator import ReportGenerator
from app.models.trustrepo_context import TrustRepoContext, SemanticContext, GraphContext, VerificationContext
from app.models.document_context import DocumentContext, Document
from app.models.repository_context import RepositoryContext
from app.models.knowledge.evidence import EvidenceChain, EvidenceItem, EvidenceSource, EvidenceStrength


def test_report_generator_document_path():
    """
    Regression test: Ensures ReportGenerator doesn't throw 'Document object has no attribute file_path'.
    """
    generator = ReportGenerator()
    
    # Setup mock context
    context = TrustRepoContext()
    context.repository_context = RepositoryContext(repository_url="https://github.com/test/test")
    context.semantic_context = SemanticContext()
    context.graph_context = GraphContext()
    context.verification_context = VerificationContext()
    
    # 1. Provide mock documents with 'path' field
    context.document_context = DocumentContext()
    context.document_context.documents = [
        Document(path="README.md", document_type="markdown", content="We use PostgreSQL for database."),
        Document(path="docs/architecture.md", document_type="markdown", content="API is GraphQL.")
    ]
    
    # 2. Add features (both documented and undocumented)
    context.semantic_context.features = ["PostgreSQL", "MongoDB"]
    
    # 3. Add evidence chains for these features to avoid INSUFFICIENT_EVIDENCE
    chain_postgres = EvidenceChain(
        chain_id="postgres_1",
        chain_type="PostgreSQL",
        reasoning_trace="Found PostgreSQL usage.",
        sequence=[
            EvidenceItem(
                source=EvidenceSource(file_path="src/db.py", line_number=10),
                context_type="STRUCTURAL",
                code_snippet="import psycopg2",
                evidence_strength=EvidenceStrength.PRIMARY
            )
        ]
    )
    chain_mongo = EvidenceChain(
        chain_id="mongo_1",
        chain_type="MongoDB",
        reasoning_trace="Found MongoDB usage.",
        sequence=[
            EvidenceItem(
                source=EvidenceSource(file_path="src/mongo.py", line_number=5),
                context_type="STRUCTURAL",
                code_snippet="import pymongo",
                evidence_strength=EvidenceStrength.PRIMARY
            )
        ]
    )
    context.semantic_context.evidence_chains = [chain_postgres, chain_mongo]

    # Act
    # If the bug exists, this will raise AttributeError
    report = generator.generate_report(context)

    # Assert
    assert report is not None
    assert report.summary.total_claims == 0
    assert len(report.undocumented_features) > 0
    
    # MongoDB is not in documents, so it should be Missing Documentation
    mongo_uf = next((uf for uf in report.undocumented_features if uf.feature_name == "MongoDB"), None)
    assert mongo_uf is not None
    assert mongo_uf.verdict == "Missing Documentation"
    
    # Documentation analysis should have the searched terms and sources
    assert "README.md" in mongo_uf.documentation_analysis or "Searched terms" in mongo_uf.documentation_analysis
    assert "MongoDB" not in report.coverage.__dict__ # coverage logic
