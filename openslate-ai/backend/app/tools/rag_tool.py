from app.services.rag_service import answer_question


def rag_tool(
    question: str,
    project_id: str | None = None,
):
    return answer_question(
        question=question,
        project_id=project_id,
    )