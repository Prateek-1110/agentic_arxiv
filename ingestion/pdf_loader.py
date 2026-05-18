import uuid
from pathlib import Path
from typing import List, Dict, Any

from pypdf import PdfReader

from config import CHUNK_SIZE, CHUNK_OVERLAP


def load_pdf(file_path: str | Path) -> List[Dict[str, Any]]:
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"PDF not found: {file_path}")

    reader = PdfReader(str(file_path))
    pages = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = text.strip()

        if not text:         
            continue

        pages.append({
            "text": text,
            "page_number": i + 1,
            "source": file_path.name,
        })

    if not pages:
        raise ValueError(f"No extractable text found in {file_path.name}. "
                         "It may be a scanned PDF.")

    return pages


def chunk_pages(
    pages: List[Dict[str, Any]],
    metadata: Dict[str, Any] = None,
) -> List[Dict[str, Any]]:
    
    metadata = metadata or {}
    chunks = []

    for page in pages:
        text = page["text"]
        start = 0

        while start < len(text):
            end = start + CHUNK_SIZE
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunk = {
                    "chunk_id": str(uuid.uuid4()),
                    "text": chunk_text,
                    "page_number": page["page_number"],
                    "source": page["source"],
                    **metadata, 
                }
                chunks.append(chunk)
            start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


def load_and_chunk(
    file_path: str | Path,
    metadata: Dict[str, Any] = None,
) -> List[Dict[str, Any]]:
   
    pages = load_pdf(file_path)
    chunks = chunk_pages(pages, metadata=metadata)
    return chunks