from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.core.config import settings

from qdrant_client.models import Filter, FieldCondition, MatchValue


COLLECTION_NAME = "openslate_chunks"

client = QdrantClient(url=settings.qdrant_url)


def ensure_collection(vector_size: int):
    collections = client.get_collections().collections
    exists = any(c.name == COLLECTION_NAME for c in collections)

    if not exists:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )


def upsert_chunks(chunks: list[dict], document_id: str, project_id: str):
    if not chunks:
        return 0

    points = []

    for idx, chunk in enumerate(chunks):
        embedding = chunk["embedding"]

        points.append(
            PointStruct(
                id=str(uuid4()),
                vector=embedding,
                payload={
                    "document_id": document_id,
                    "project_id": project_id,
                    "chunk_index": idx,
                    "page": chunk.get("page"),
                    "type": chunk.get("type"),
                    "content": chunk.get("content")
                }
            )
        )

    ensure_collection(len(chunks[0]["embedding"]))

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    return len(points)

def delete_document_chunks(document_id: str):
    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id)
                )
            ]
        )
    )