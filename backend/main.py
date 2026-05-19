import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import ingest, query, session
from config import API_HOST, API_PORT, ALLOWED_ORIGINS


app = FastAPI(
    title="Agentic Arxiv RAG",
    description="Chat with Arxiv papers using an agentic RAG pipeline.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # safer for deployment initially
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router)
app.include_router(query.router)
app.include_router(session.router)


@app.get("/")
async def root():
    return {"message": "Backend running"}


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
       port=int(API_PORT)
    )