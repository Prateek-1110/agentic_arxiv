import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Base paths ────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR / "storage"
CHROMA_DIR = STORAGE_DIR / "chroma_db"

# Create dirs if they don't exist
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# ── LLM ───────────────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")  # swap to gemini-pro if needed

# ── Embedding model ───────────────────────────────────────────────────────────
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)  # same model you used in your notebook
EMBEDDING_DIMENSION = 384  # MiniLM-L6-v2 output dim

# ── Reranker ──────────────────────────────────────────────────────────────────
# RERANKER_MODEL = os.getenv(
#     "RERANKER_MODEL", "cross-encoder/ms-marco-TinyBERT-L-2-v2"
# )  # same cross-encoder from your notebook
RERANKER_MODEL = None  # set to None for now since cross-encoder is slow and not critical for demo
# ── ChromaDB ──────────────────────────────────────────────────────────────────
CHROMA_COLLECTION_NAME = "arxiv_papers"

# ── Chunking ──────────────────────────────────────────────────────────────────
CHUNK_SIZE = 500        # characters per chunk (same as your notebook)
CHUNK_OVERLAP = 100     # overlap between consecutive chunks

# ── Retrieval ─────────────────────────────────────────────────────────────────
TOP_K_RETRIEVAL = 8     # how many chunks to pull from vectorstore before reranking
TOP_K_RERANKED = 3      # how many chunks to pass to LLM after reranking

# ── Arxiv ─────────────────────────────────────────────────────────────────────
ARXIV_MAX_RESULTS = 3   # max papers fetched when agent searches Arxiv by keyword

# ── Memory ────────────────────────────────────────────────────────────────────
MAX_HISTORY_TURNS = 10  # max conversation turns kept per session (older ones dropped)

# ── FastAPI ───────────────────────────────────────────────────────────────────
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("PORT", 10000))
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "https://agentic-arxiv.vercel.app"
).split(",")
# ^ 5500 is Live Server default port in VS Code