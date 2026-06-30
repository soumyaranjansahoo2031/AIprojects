from fastapi import APIRouter

from app.schemas.retrieval import RetrievalRequest
from app.services.embedding_service import generate_embedding
from app.services.qdrant_service import search_chunks


router = APIRouter(
    prefix="/retrieval",
    tags=["Retrieval"],
)


@router.post("/search")
def search_documents(payload: RetrievalRequest):
    query_embedding = generate_embedding(payload.query)

    results = search_chunks(
        query_embedding=query_embedding,
        project_id=payload.project_id,
        limit=payload.limit,
    )

    return {
        "query": payload.query,
        "count": len(results),
        "results": results,
    }