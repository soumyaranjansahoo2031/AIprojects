from fastapi import APIRouter
from pydantic import BaseModel

from app.agents.rag_agent import run_rag_agent


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


class ChatRequest(BaseModel):
    question: str
    project_id: str | None = None


@router.post("/")
def chat(payload: ChatRequest):
    result = run_rag_agent(
        question=payload.question,
        project_id=payload.project_id,
    )

    return {
        "answer": result["answer"],
        "sources": result["sources"],
    }