from pydantic import BaseModel


class RetrievalRequest(BaseModel):
    query: str
    project_id: str | None = None
    limit: int = 5