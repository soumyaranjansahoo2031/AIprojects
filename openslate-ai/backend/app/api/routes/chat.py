from fastapi import APIRouter
from pydantic import BaseModel

from app.services.rag_service import answer_question


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


class ChatRequest(BaseModel):
    question: str
    project_id: str | None = None


@router.post("/")
def chat(payload: ChatRequest):
    return answer_question(
        payload.question,
        payload.project_id,
    )