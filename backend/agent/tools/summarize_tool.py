from typing import Dict, Any

from retrieval.vectorstore import query_vectorstore
from retrieval.reranker import rerank
from agent.tools.vectorstore_tool import format_context
from agent.prompts import SUMMARIZE_PROMPT


def summarize_paper(arxiv_id: str, llm_fn) -> Dict[str, Any]:
    chunks = query_vectorstore(query=arxiv_id, top_k=20)
    paper_chunks = [c for c in chunks if c.get("arxiv_id") == arxiv_id]

    if not paper_chunks:
        return {
            "status": "error",
            "message": f"No ingested content found for arxiv_id: {arxiv_id}",
        }

    reranked = rerank(arxiv_id, paper_chunks, top_k=8)
    context = format_context(reranked)

    title = reranked[0].get("title", "Unknown")
    authors = reranked[0].get("authors", "Unknown")

    prompt = SUMMARIZE_PROMPT.format(
        title=title,
        authors=authors,
        context=context,
    )

    summary = llm_fn(prompt)

    return {
        "status": "ok",
        "arxiv_id": arxiv_id,
        "title": title,
        "authors": authors,
        "summary": summary,
    }