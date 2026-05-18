import time
import urllib.request
from pathlib import Path
from typing import List, Dict, Any
import xml.etree.ElementTree as ET

from config import ARXIV_MAX_RESULTS, STORAGE_DIR

ARXIV_API_BASE = "http://export.arxiv.org/api/query"
ARXIV_NS = "{http://www.w3.org/2005/Atom}"
PDF_DOWNLOAD_DIR = STORAGE_DIR / "arxiv_pdfs"
PDF_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _parse_feed(xml_bytes: bytes) -> List[Dict[str, Any]]:
    root = ET.fromstring(xml_bytes)
    papers = []

    for entry in root.findall(f"{ARXIV_NS}entry"):
        arxiv_id_raw = entry.findtext(f"{ARXIV_NS}id", "")
        arxiv_id = arxiv_id_raw.split("/abs/")[-1].strip()

        title = entry.findtext(f"{ARXIV_NS}title", "").replace("\n", " ").strip()
        summary = entry.findtext(f"{ARXIV_NS}summary", "").replace("\n", " ").strip()

        authors = [
            a.findtext(f"{ARXIV_NS}name", "")
            for a in entry.findall(f"{ARXIV_NS}author")
        ]

        pdf_url = ""
        for link in entry.findall(f"{ARXIV_NS}link"):
            if link.attrib.get("title") == "pdf":
                pdf_url = link.attrib.get("href", "")
                break

        papers.append({
            "arxiv_id": arxiv_id,
            "title": title,
            "authors": ", ".join(authors),
            "summary": summary,
            "pdf_url": pdf_url,
        })

    return papers


def search_arxiv(query: str, max_results: int = ARXIV_MAX_RESULTS) -> List[Dict[str, Any]]:
    url = (
        f"{ARXIV_API_BASE}?search_query=all:{urllib.parse.quote(query)}"
        f"&start=0&max_results={max_results}&sortBy=relevance"
    )
    with urllib.request.urlopen(url) as resp:
        xml_bytes = resp.read()
    return _parse_feed(xml_bytes)


def fetch_by_id(arxiv_id: str) -> Dict[str, Any]:
    clean_id = arxiv_id.strip().split("v")[0]
    url = f"{ARXIV_API_BASE}?id_list={clean_id}"
    with urllib.request.urlopen(url) as resp:
        xml_bytes = resp.read()
    results = _parse_feed(xml_bytes)
    if not results:
        raise ValueError(f"No paper found for arxiv_id: {arxiv_id}")
    return results[0]


def download_pdf(paper: Dict[str, Any]) -> Path:
    arxiv_id_safe = paper["arxiv_id"].replace("/", "_")
    dest = PDF_DOWNLOAD_DIR / f"{arxiv_id_safe}.pdf"

    if dest.exists():
        return dest

    pdf_url = paper.get("pdf_url", "")
    if not pdf_url:
        raise ValueError(f"No PDF URL for paper: {paper['arxiv_id']}")

    time.sleep(3)
    urllib.request.urlretrieve(pdf_url, dest)
    return dest