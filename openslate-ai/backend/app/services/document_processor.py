from pathlib import Path
import json

from app.services.partition_service import partition_document
from app.services.chunking_service import chunk_by_title
from app.services.embedding_service import generate_embedding
from app.services.qdrant_service import upsert_chunks


def save_json(data, output_path: Path) -> str:
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False,
        )

    return str(output_path)


def process_document(
    document_id: str,
    project_id: str,
    file_path: str,
) -> dict:
    file_path_obj = Path(file_path)
    project_dir = file_path_obj.parent.parent

    metadata_dir = project_dir / "metadata"
    chunks_dir = project_dir / "chunks"

    elements = partition_document(file_path)

    partition_path = save_json(
        elements,
        metadata_dir / f"{document_id}_partition.json",
    )

    chunks = chunk_by_title(elements)

    for chunk in chunks:
        searchable_text = f"{chunk.get('title', '')}\n{chunk.get('content', '')}"
        chunk["embedding"] = generate_embedding(searchable_text)

    chunks_path = save_json(
        chunks,
        chunks_dir / f"{document_id}_semantic_chunks.json",
    )

    vector_count = upsert_chunks(
        chunks=chunks,
        document_id=document_id,
        project_id=project_id,
    )

    return {
        "partition_path": partition_path,
        "chunks_path": chunks_path,
        "element_count": len(elements),
        "chunk_count": len(chunks),
        "vector_count": vector_count,
    }