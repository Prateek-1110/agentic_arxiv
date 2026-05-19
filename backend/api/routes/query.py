from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agent.agent_runner import run_agent
from retrieval.vectorstore import query_vectorstore
from retrieval.reranker import rerank
from agent.tools.vectorstore_tool import format_context
from memory.session_store import create_session

router = APIRouter(prefix="/query", tags=["query"])


class QueryRequest(BaseModel):
    question: str
    session_id: str | None = None


class AgentQueryRequest(BaseModel):
    question: str
    session_id: str


@router.post("/")
async def plain_query(body: QueryRequest):
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    chunks = query_vectorstore(body.question)
    if not chunks:
        return {"answer": "No relevant content found in ingested papers.", "sources": []}

    reranked = rerank(body.question, chunks)
    context = format_context(reranked)

    sources = [
        {
            "title": c.get("title", ""),
            "arxiv_id": c.get("arxiv_id", ""),
            "page_number": c.get("page_number", ""),
        }
        for c in reranked
    ]

    return {"context": context, "sources": sources}


@router.post("/agent")
async def agent_query(body: AgentQueryRequest):
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    result = run_agent(query=body.question, session_id=body.session_id)
    return result


@router.post("/session/new")
async def new_session():
    session_id = create_session()
    return {"session_id": session_id}