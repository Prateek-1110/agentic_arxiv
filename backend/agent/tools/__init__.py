from typing import List, Dict, Any

from retrieval.vectorstore import query_vectorstore
from retrieval.reranker import rerank


def search_vectorstore(query: str) -> List[Dict[str, Any]]:
    raw_chunks = query_vectorstore(query)

    if not raw_chunks:
        return []

    reranked = rerank(query, raw_chunks)
    return reranked


def format_context(chunks: List[Dict[str, Any]]) -> str:
    if not chunks:
        return ""

    parts = []
    for chunk in chunks:
        title = chunk.get("title", chunk.get("source", "Unknown"))
        page = chunk.get("page_number", "?")
        parts.append(f"[{title} | Page {page}]\n{chunk['text']}")

    return "\n\n---\n\n".join(parts)