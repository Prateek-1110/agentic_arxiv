from typing import List
from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print(f"[embedder] Loading model: {EMBEDDING_MODEL}")
        _model = SentenceTransformer(EMBEDDING_MODEL)
        print(f"[embedder] Model loaded. Dimension: {_model.get_sentence_embedding_dimension()}")
    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []

    model = get_model()

    vectors = model.encode(
        texts,
        show_progress_bar=len(texts) > 20,  
        convert_to_numpy=False,          
    )

    return [v.tolist() for v in vectors]


def embed_query(query: str) -> List[float]:
    if not query or not query.strip():
        raise ValueError("[embedder] Query string is empty.")

    result = embed_texts([query])
    return result[0]