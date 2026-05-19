import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from ingestion.pdf_loader import load_and_chunk
from ingestion.arxiv_fetcher import fetch_by_id, search_arxiv, download_pdf
from retrieval.vectorstore import add_chunks, paper_already_ingested, list_ingested_papers
from config import STORAGE_DIR

router = APIRouter(prefix="/ingest", tags=["ingest"])

UPLOAD_DIR = STORAGE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class ArxivIngestRequest(BaseModel):
    arxiv_id_or_query: str


@router.post("/pdf")
async def ingest_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    dest = UPLOAD_DIR / f"{uuid.uuid4()}_{file.filename}"
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        chunks = load_and_chunk(dest, metadata={"source": file.filename})
        added = add_chunks(chunks)
    except ValueError as e:
        dest.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=str(e))

    return {
        "status": "ingested",
        "filename": file.filename,
        "chunks_added": added,
    }


@router.post("/arxiv")
async def ingest_arxiv(body: ArxivIngestRequest):
    query = body.arxiv_id_or_query.strip()

    is_id = _looks_like_arxiv_id(query)
    paper = fetch_by_id(query) if is_id else _search_top(query)

    if not paper:
        raise HTTPException(status_code=404, detail=f"No paper found for: {query}")

    arxiv_id = paper["arxiv_id"]

    if paper_already_ingested(arxiv_id):
        return {"status": "already_ingested", "arxiv_id": arxiv_id, "title": paper["title"]}

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


@router.get("/list")
async def list_papers():
    return {"papers": list_ingested_papers()}


def _looks_like_arxiv_id(text: str) -> bool:
    import re
    return bool(re.match(r"^\d{4}\.\d{4,5}(v\d+)?$", text))


def _search_top(query: str):
    results = search_arxiv(query, max_results=1)
    return results[0] if results else None