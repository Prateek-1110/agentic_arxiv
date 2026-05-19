import urllib.parse
from typing import List, Dict, Any

import chromadb
from chromadb.config import Settings

from config import CHROMA_DIR, CHROMA_COLLECTION_NAME, TOP_K_RETRIEVAL
from ingestion.embedder import embed_texts, embed_query


from typing import Any

_client: Any = None
_collection = None


def get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
        _collection = _client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def add_chunks(chunks: List[Dict[str, Any]]) -> int:
    collection = get_collection()

    ids = [c["chunk_id"] for c in chunks]
    texts = [c["text"] for c in chunks]
    metadatas = [
        {k: v for k, v in c.items() if k not in ("chunk_id", "text")}
        for c in chunks
    ]

    existing = set(collection.get(ids=ids)["ids"])
    new_indices = [i for i, cid in enumerate(ids) if cid not in existing]

    if not new_indices:
        return 0

    new_ids = [ids[i] for i in new_indices]
    new_texts = [texts[i] for i in new_indices]
    new_metadatas = [metadatas[i] for i in new_indices]
    new_embeddings = embed_texts(new_texts)

    collection.add(
        ids=new_ids,
        documents=new_texts,
        embeddings=new_embeddings,
        metadatas=new_metadatas,
    )

    return len(new_ids)


def query_vectorstore(query: str, top_k: int = TOP_K_RETRIEVAL) -> List[Dict[str, Any]]:
    collection = get_collection()

    if collection.count() == 0:
        return []

    query_vector = embed_query(query)

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({
            "text": doc,
            "score": round(1 - dist, 4),
            **meta,
        })

    return chunks


def list_ingested_papers() -> List[Dict[str, str]]:
    collection = get_collection()
    all_items = collection.get(include=["metadatas"])

    seen = set()
    papers = []
    for meta in all_items["metadatas"]:
        pid = meta.get("arxiv_id") or meta.get("source", "")
        if pid and pid not in seen:
            seen.add(pid)
            papers.append({
                "arxiv_id": meta.get("arxiv_id", ""),
                "title": meta.get("title", ""),
                "authors": meta.get("authors", ""),
                "source": meta.get("source", ""),
            })

    return papers


def paper_already_ingested(arxiv_id: str) -> bool:
    collection = get_collection()
    results = collection.get(
        where={"arxiv_id": {"$eq": arxiv_id}},
        limit=1,
    )
    return len(results["ids"]) > 0