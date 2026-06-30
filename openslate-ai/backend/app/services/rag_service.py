import requests

from app.services.embedding_service import generate_embedding
from app.services.qdrant_service import search_chunks


OLLAMA_CHAT_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "qwen2.5-coder:14b"


def answer_question(
    question: str,
    project_id: str | None = None,
):
    query_embedding = generate_embedding(question)

    chunks = search_chunks(
        query_embedding=query_embedding,
        project_id=project_id,
        limit=5,
    )

    context = "\n\n".join(
        [
            chunk["payload"]["content"]
            for chunk in chunks
        ]
    )

    prompt = f"""
You are a helpful AI assistant.

Answer ONLY using the provided context.

If the answer is not present in the context, say:
"I could not find the answer in the uploaded documents."

Context:
{context}

Question:
{question}

Answer:
"""

    response = requests.post(
        OLLAMA_CHAT_URL,
        json={
            "model": LLM_MODEL,
            "prompt": prompt,
            "stream": False,
        },
        timeout=300,
    )

    response.raise_for_status()

    answer = response.json()["response"]

    return {
        "answer": answer,
        "sources": chunks,
    }