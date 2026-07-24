import uuid
import json
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from src.core.config import get_settings
from src.core.embeddings import embed_documents, embed_query, rerank


class QdrantStore:
    def __init__(self):
        settings = get_settings()
        self.client = QdrantClient(url=settings.qdrant_url)
        self.collection = settings.qdrant_collection
        self._ensure_collection()

    def _ensure_collection(self):
        collections = [c.name for c in self.client.get_collections().collections]
        if self.collection not in collections:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
            )

    def add_documents(self, docs: list[dict]):
        texts = [d["content"] for d in docs]
        vectors = embed_documents(texts)

        points = []
        for i, (doc, vec) in enumerate(zip(docs, vectors)):
            point_id = str(uuid.uuid4())
            points.append(
                PointStruct(
                    id=point_id,
                    vector=vec,
                    payload={
                        "content": doc["content"],
                        "source": doc.get("source", ""),
                        "doc_type": doc.get("doc_type", "unknown"),
                        "metadata": json.dumps(doc.get("metadata", {})),
                    },
                )
            )

        self.client.upsert(collection_name=self.collection, points=points)
        return len(points)

    def search(self, query: str, top_k: int = 10, filter_source: str = None) -> list[dict]:
        query_vec = embed_query(query)

        search_filter = None
        if filter_source:
            search_filter = Filter(
                must=[FieldCondition(key="source", match=MatchValue(value=filter_source))]
            )

        results = self.client.search(
            collection_name=self.collection,
            query_vector=query_vec,
            limit=top_k * 2,
            query_filter=search_filter,
        )

        documents = [r.payload["content"] for r in results]
        reranked = rerank(query, documents, top_k=top_k)

        return reranked

    def delete_by_source(self, source: str):
        self.client.delete(
            collection_name=self.collection,
            points_selector=Filter(
                must=[FieldCondition(key="source", match=MatchValue(value=source))]
            ),
        )

    def count(self) -> int:
        info = self.client.count(collection_name=self.collection)
        return info.count
