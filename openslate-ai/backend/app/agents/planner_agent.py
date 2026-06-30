def route_question(
    question: str,
    project_id: str | None,
):
    if project_id:
        return "rag"

    return "web"