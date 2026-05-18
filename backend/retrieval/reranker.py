from typing import List, Dict, Any

from sentence_transformers import CrossEncoder

from config import RERANKER_MODEL, TOP_K_RERANKED


_reranker: CrossEncoder | None = None


def get_reranker() -> CrossEncoder:
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder(RERANKER_MODEL)
    return _reranker


def rerank(query: str, chunks: List[Dict[str, Any]], top_k: int = TOP_K_RERANKED) -> List[Dict[str, Any]]:
    if not chunks:
        return []

    reranker = get_reranker()
    pairs = [(query, chunk["text"]) for chunk in chunks]
    scores = reranker.predict(pairs)

    for chunk, score in zip(chunks, scores):
        chunk["rerank_score"] = round(float(score), 4)

    ranked = sorted(chunks, key=lambda x: x["rerank_score"], reverse=True)
    return ranked[:top_k]