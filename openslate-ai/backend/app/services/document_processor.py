from pathlib import Path
import json
import fitz

from app.services.embedding_service import generate_embedding
from app.services.qdrant_service import upsert_chunks


def extract_text_from_pdf(file_path: str) -> list[dict]:
    doc = fitz.open(file_path)
    pages = []

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        pages.append({
            "page": page_num,
            "text": text.strip()
        })

    return pages


def chunk_text(
    pages: list[dict],
    chunk_size: int = 1000,
    overlap: int = 200
) -> list[dict]:
    chunks = []

    for page in pages:
        text = page["text"]
        page_num = page["page"]

        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end].strip()

            if chunk:
                chunks.append({
                    "page": page_num,
                    "content": chunk,
                    "type": "text"
                })

            start += chunk_size - overlap

    return chunks


def save_chunks_file(
    chunks: list[dict],
    document_id: str,
    file_path: str
) -> str:
    file_path_obj = Path(file_path)
    project_dir = file_path_obj.parent.parent
    chunks_dir = project_dir / "chunks"

    chunks_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = chunks_dir / f"{document_id}_chunks.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            chunks,
            f,
            indent=2,
            ensure_ascii=False
        )

    return str(output_path)


def process_document(
    document_id: str,
    project_id: str,
    file_path: str
) -> dict:
    pages = extract_text_from_pdf(file_path)
    chunks = chunk_text(pages)

    for chunk in chunks:
        chunk["embedding"] = generate_embedding(
            chunk["content"]
        )

    chunks_path = save_chunks_file(
        chunks,
        document_id,
        file_path
    )

    vector_count = upsert_chunks(
        chunks,
        document_id,
        project_id
    )

    return {
        "chunks_path": chunks_path,
        "chunk_count": len(chunks),
        "vector_count": vector_count
    }