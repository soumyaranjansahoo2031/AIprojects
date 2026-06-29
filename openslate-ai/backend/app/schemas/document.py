from datetime import datetime
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: str
    project_id: str
    filename: str
    file_path: str
    content_type: str
    file_size: int
    status: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }