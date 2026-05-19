from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.dependencies import preload_models
from api.routes import ingest, query, session
from config import API_HOST, API_PORT, ALLOWED_ORIGINS


@asynccontextmanager
async def lifespan(app: FastAPI):
    preload_models()
    yield


app = FastAPI(
    title="Agentic Arxiv RAG",
    description="Chat with Arxiv papers using an agentic RAG pipeline.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router)
app.include_router(query.router)
app.include_router(session.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host=API_HOST, port=API_PORT, reload=True)