import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

STORAGE_DIR = BASE_DIR / "storage"
CHROMA_DIR = STORAGE_DIR / "chroma_db"

STORAGE_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is missing in .env")

if not GEMINI_MODEL:
    raise ValueError("GEMINI_MODEL is missing in .env")

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2"
)

EMBEDDING_DIMENSION = 384

RERANKER_MODEL = None

CHROMA_COLLECTION_NAME = "arxiv_papers"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

TOP_K_RETRIEVAL = 8
TOP_K_RERANKED = 3

ARXIV_MAX_RESULTS = 3

MAX_HISTORY_TURNS = 10

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("PORT", 8000))

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5500,https://agentic-arxiv.vercel.app"
).split(",")