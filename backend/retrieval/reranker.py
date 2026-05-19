from typing import List, Dict, Any

from sentence_transformers import CrossEncoder

from config import RERANKER_MODEL, TOP_K_RERANKED


_reranker: CrossEncoder | None = None


def get_reranker():
    global _reranker

    if RERANKER_MODEL is None:
        return None

    if _reranker is None:
        print(f"[reranker] Loading model: {RERANKER_MODEL}")
        _reranker = CrossEncoder(RERANKER_MODEL)

    return _reranker


def rerank(
    query: str,
    chunks: List[Dict[str, Any]],
    top_k: int = TOP_K_RERANKED
) -> List[Dict[str, Any]]:

    if not chunks:
        return []

    reranker = get_reranker()

    # If reranker disabled, return top chunks directly
    if reranker is None:
        return chunks[:top_k]

    pairs = [(query, chunk["text"]) for chunk in chunks]
    scores = reranker.predict(pairs)

    for chunk, score in zip(chunks, scores):
        chunk["rerank_score"] = round(float(score), 4)

    ranked = sorted(
        chunks,
        key=lambda x: x["rerank_score"],
        reverse=True
    )

    return ranked[:top_k]