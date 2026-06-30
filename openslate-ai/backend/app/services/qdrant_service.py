from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)

from app.core.config import settings


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
                distance=Distance.COSINE,
            ),
        )


def upsert_chunks(
    chunks: list[dict],
    document_id: str,
    project_id: str,
):
    if not chunks:
        return 0

    ensure_collection(len(chunks[0]["embedding"]))

    points = []

    for idx, chunk in enumerate(chunks):
        points.append(
            PointStruct(
                id=str(uuid4()),
                vector=chunk["embedding"],
                payload={
                    "document_id": document_id,
                    "project_id": project_id,
                    "chunk_index": idx,
                    "title": chunk.get("title"),
                    "content": chunk.get("content"),
                    "pages": chunk.get("pages"),
                    "types": chunk.get("types"),
                },
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )

    return len(points)


def delete_document_chunks(document_id: str):
    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id),
                )
            ]
        ),
    )


def search_chunks(
    query_embedding: list[float],
    project_id: str | None = None,
    limit: int = 5,
):
    query_filter = None

    if project_id:
        query_filter = Filter(
            must=[
                FieldCondition(
                    key="project_id",
                    match=MatchValue(value=project_id),
                )
            ]
        )

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        query_filter=query_filter,
        limit=limit,
    ).points

    return [
        {
            "score": result.score,
            "payload": result.payload,
        }
        for result in results
    ]