import uuid
from typing import List
from app.models.knowledge.evidence import EvidenceChain, EvidenceItem, EvidenceType, EvidenceStrength, EvidenceSource
from app.services.analysis.retrievers.base_retriever import BaseEvidenceRetriever
from app.models.knowledge.feature_instance import FeatureInstance


class DatabaseRetriever(BaseEvidenceRetriever):
    """
    Retrieves evidence separately for ORM, Database, Connection Pooling, Migrations.
    """

    def __init__(self, repo, mode: str):
        super().__init__(repo)
        self.mode = mode

    def retrieve(self, feature: FeatureInstance) -> List[EvidenceChain]:
        items = []
        if self.mode == "orm":
            items = self._detect_orm()
        elif self.mode == "database":
            items = self._detect_database()
        elif self.mode == "pooling":
            items = self._detect_pooling()
        elif self.mode == "migration":
            items = self._detect_migration()

        if items:
            chain = EvidenceChain(
                chain_id=f"db_{self.mode}_{uuid.uuid4()}",
                chain_type=f"{self.mode.upper()} Evidence",
                retrieval_strategy=f"{self.mode.capitalize()} Structural Detection",
                sequence=items,
                graph_path=f"AST -> {self.mode.capitalize()}",
                confidence=0.9,
                reasoning_trace=f"Found concrete {self.mode} evidence."
            )
            return [chain]
        return []

    def _detect_orm(self) -> List[EvidenceItem]:
        query = """
        MATCH (c:Class)
        WHERE c.name CONTAINS 'Model' OR c.name CONTAINS 'Entity'
        MATCH (c)-[:INHERITS]->(base)
        RETURN c.name as name, base.name as base_name, c.file_path as file, c.start_line as line
        LIMIT 5
        """
        results = self.repo.conn.query(query, {})
        items = []
        for r in (results or []):
            if r.get("file"):
                items.append(EvidenceItem(
                    source=EvidenceSource(file_path=r.get("file"), line_number=r.get("line")),
                    evidence_type=EvidenceType.STRUCTURAL,
                    symbol=r.get("name"),
                    context_type="orm_model",
                    evidence_strength=EvidenceStrength.PRIMARY,
                    extraction_method="GraphStructuralQuery",
                    explanation=f"ORM Model '{r.get('name')}' inheriting from '{r.get('base_name')}'."
                ))
        return items

    def _detect_database(self) -> List[EvidenceItem]:
        query = """
        MATCH (i:Import)
        WHERE i.name CONTAINS 'psycopg' OR i.name CONTAINS 'pg' OR i.name CONTAINS 'mysql' OR i.name CONTAINS 'sqlite'
        RETURN i.name as name, i.file_path as file, i.start_line as line
        LIMIT 5
        """
        results = self.repo.conn.query(query, {})
        items = []
        for r in (results or []):
            if r.get("file"):
                items.append(EvidenceItem(
                    source=EvidenceSource(file_path=r.get("file"), line_number=r.get("line")),
                    evidence_type=EvidenceType.IMPORT,
                    symbol=r.get("name"),
                    context_type="database_driver",
                    evidence_strength=EvidenceStrength.PRIMARY,
                    extraction_method="GraphASTQuery",
                    explanation=f"Database driver import '{r.get('name')}'."
                ))
        return items

    def _detect_pooling(self) -> List[EvidenceItem]:
        query = """
        MATCH (n)
        WHERE n.name CONTAINS 'Pool' OR n.name CONTAINS 'ConnectionPool'
        RETURN labels(n)[0] as label, n.name as name, n.file_path as file, n.start_line as line
        LIMIT 5
        """
        results = self.repo.conn.query(query, {})
        items = []
        for r in (results or []):
            if r.get("file"):
                items.append(EvidenceItem(
                    source=EvidenceSource(file_path=r.get("file"), line_number=r.get("line")),
                    evidence_type=EvidenceType.AST,
                    symbol=r.get("name"),
                    context_type="connection_pool",
                    evidence_strength=EvidenceStrength.PRIMARY,
                    extraction_method="GraphASTQuery",
                    explanation=f"Connection pool construct '{r.get('name')}'."
                ))
        return items

    def _detect_migration(self) -> List[EvidenceItem]:
        query = """
        MATCH (i:Import)
        WHERE i.name CONTAINS 'alembic' OR i.name CONTAINS 'flyway' OR i.name CONTAINS 'liquibase' OR i.name CONTAINS 'migrate'
        RETURN i.name as name, i.file_path as file, i.start_line as line
        LIMIT 5
        """
        results = self.repo.conn.query(query, {})
        items = []
        for r in (results or []):
            if r.get("file"):
                items.append(EvidenceItem(
                    source=EvidenceSource(file_path=r.get("file"), line_number=r.get("line")),
                    evidence_type=EvidenceType.IMPORT,
                    symbol=r.get("name"),
                    context_type="database_migration",
                    evidence_strength=EvidenceStrength.PRIMARY,
                    extraction_method="GraphASTQuery",
                    explanation=f"Migration tool import '{r.get('name')}'."
                ))
        return items
