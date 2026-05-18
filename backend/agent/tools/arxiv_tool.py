from typing import Dict, Any

from ingestion.arxiv_fetcher import fetch_by_id, search_arxiv, download_pdf
from ingestion.pdf_loader import load_and_chunk
from retrieval.vectorstore import add_chunks, paper_already_ingested


def fetch_and_ingest_arxiv(arxiv_id_or_query: str) -> Dict[str, Any]:
    is_arxiv_id = _looks_like_arxiv_id(arxiv_id_or_query)

    if is_arxiv_id:
        paper = fetch_by_id(arxiv_id_or_query)
    else:
        results = search_arxiv(arxiv_id_or_query, max_results=1)
        if not results:
            return {"status": "error", "message": f"No papers found for: {arxiv_id_or_query}"}
        paper = results[0]

    arxiv_id = paper["arxiv_id"]

    if paper_already_ingested(arxiv_id):
        return {
            "status": "already_ingested",
            "arxiv_id": arxiv_id,
            "title": paper["title"],
        }

    pdf_path = download_pdf(paper)

    metadata = {
        "arxiv_id": arxiv_id,
        "title": paper["title"],
        "authors": paper["authors"],
    }

    chunks = load_and_chunk(pdf_path, metadata=metadata)
    added = add_chunks(chunks)

    return {
        "status": "ingested",
        "arxiv_id": arxiv_id,
        "title": paper["title"],
        "authors": paper["authors"],
        "chunks_added": added,
    }


def _looks_like_arxiv_id(text: str) -> bool:
    import re
    text = text.strip()
    return bool(re.match(r"^\d{4}\.\d{4,5}(v\d+)?$", text))