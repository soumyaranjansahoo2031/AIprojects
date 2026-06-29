from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    HTTPException
)

from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.project import Project
from app.models.document import Document
from app.schemas.document import DocumentResponse
from app.services.storage_service import save_document

from app.services.document_processor import process_document    

from app.core.constants import DocumentStatus

from pathlib import Path
from app.services.qdrant_service import delete_document_chunks


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.post(
    "/{project_id}",
    response_model=DocumentResponse
)
def upload_document(
    project_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    file_path = save_document(
        project_id,
        file
    )

    document = Document(
        project_id=project_id,
        filename=file.filename,
        file_path=file_path,
        content_type=file.content_type,
        file_size=0
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document

@router.get("/", response_model=list[DocumentResponse])
def list_documents(
    db: Session = Depends(get_db)
):
    return (
        db.query(Document)
        .order_by(Document.created_at.desc())
        .all()
    )

@router.post("/{document_id}/process")
def process_uploaded_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    document.status = DocumentStatus.PROCESSING
    db.commit()

    result = process_document(
        document.id,
        document.project_id,
        document.file_path
    )

    document.status = DocumentStatus.PROCESSED
    db.commit()
    db.refresh(document)

    return {
        "message": "Document processed successfully",
        "document_id": document.id,
        "status": document.status,
        "chunks_path": result["chunks_path"],
        "chunk_count": result["chunk_count"],
        "vector_count": result["vector_count"]
    }

@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # Delete vectors from Qdrant
    delete_document_chunks(document_id)

    # Delete file from local storage
    if document.file_path and Path(document.file_path).exists():
        Path(document.file_path).unlink()

    # Delete document row from database
    db.delete(document)
    db.commit()

    return {
        "message": "Document deleted successfully",
        "document_id": document_id
    }