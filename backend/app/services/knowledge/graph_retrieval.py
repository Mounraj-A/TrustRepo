from app.models.claim import Claim
from app.models.knowledge.evidence import EvidenceCandidate
from app.repositories.graph_repository import GraphRepository
from typing import List


class GraphRetrievalEngine:
    """Searches the Neo4j Knowledge Graph using Semantic Features."""

    def __init__(self, repo: GraphRepository = None):
        self.repo = repo or GraphRepository()

    def retrieve(self, claim: Claim) -> List[EvidenceCandidate]:
        candidates = []

        # Fallback to basic keyword extraction since metadata is deprecated
        features = [w for w in claim.text.split() if len(w) > 4]

        # Deduplicate
        features = list(set(features))

        for feat in features:
            if not feat or len(feat) < 3:
                continue

            query = """
            MATCH (n)
            WHERE toLower(n.name) CONTAINS toLower($feat)
            OPTIONAL MATCH (n)-[r]->(m)
            RETURN n.name as subject, labels(n)[0] as node_label, type(r) as rel, m.name as obj, n.file_path as file, n.start_line as line LIMIT 5
            """
            try:
                res = self.repo.conn.query(query, {"feat": feat})
                for record in res:
                    rel = record.get('rel')
                    obj = record.get('obj')
                    if rel and obj:
                        content = f"{record.get('subject')} -[{rel}]-> {obj}"
                    else:
                        content = f"Node found: {record.get('subject')}"

                    candidates.append(EvidenceCandidate(
                        source_engine="graph",
                        content=content,
                        file_path=record.get("file") or "unknown",
                        content_snippet=f"Line {record.get('line') or '?'}",
                        metadata={"feature": feat}
                    ))
            except Exception as e:
                print(f"Graph retrieval failed for {feat}: {e}")

        return candidates
