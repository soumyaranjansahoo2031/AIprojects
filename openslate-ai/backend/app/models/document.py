from datetime import datetime
import uuid

from sqlalchemy import String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base

from app.core.constants import DocumentStatus


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    project_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("projects.id")
    )

    filename: Mapped[str] = mapped_column(String)

    file_path: Mapped[str] = mapped_column(String)

    content_type: Mapped[str] = mapped_column(String)

    file_size: Mapped[int] = mapped_column(Integer)

    status: Mapped[str] = mapped_column(
        String,
        default=DocumentStatus.UPLOADED
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )