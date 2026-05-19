<div align="center">

# Arxiv / rag

### Talk to research papers. Actually understand them.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-agentic--arxiv.vercel.app-6366f1?style=flat-square)](https://agentic-arxiv.vercel.app)
[![FastAPI](https://img.shields.io/badge/FastAPI-backend-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)

*Paste an Arxiv ID. Upload a PDF. Ask anything — across one paper or fifty.*  
*No prompt engineering required. The agent figures out what to do.*

</div>

---

## What makes this different

Most RAG demos make you manage the retrieval yourself — pick a paper, ask about it, hope for the best. This one doesn't.

You just ask a question. The agent decides in real time whether to search what's already ingested, fetch a new paper from Arxiv on the fly, summarize something, or answer directly. No `@tool` decorators. No LangChain. Every component is written from scratch.

---

## Under the hood

Every query runs through a tight two-step loop:

```
Your question
      │
      ▼
  Agent Router  (Gemini reads the question → picks a tool)
      │
      ├─ search_vectorstore      ChromaDB → cross-encoder rerank → cited answer
      ├─ fetch_and_ingest_arxiv  download PDF → embed → search → cited answer
      ├─ summarize_paper         retrieve all chunks → structured summary
      └─ answer_directly         no retrieval needed → straight answer
```

**Step 1 — Route.** Gemini reads your query and returns structured JSON naming the right tool and its arguments.

**Step 2 — Generate.** Retrieved chunks (post-reranking) become context. Gemini writes a cited answer grounded in the paper text.

That's the whole loop. Simple enough to debug. Powerful enough to handle messy multi-paper workflows.

---

## Stack

| Layer | Choice | Why |
|-------|--------|-----|
| LLM | Gemini 1.5 Flash | Fast, cheap, solid at structured output |
| Embeddings | `all-MiniLM-L6-v2` (384d) | Lightweight, accurate enough |
| Reranker | `ms-marco-TinyBERT-L-2-v2` | Dramatic precision boost at minimal cost |
| Vectorstore | ChromaDB | Persistent, cosine similarity, zero infra |
| Backend | FastAPI + Uvicorn | Clean async, auto docs at `/docs` |
| Frontend | Vanilla HTML/CSS/JS | No build step, fast, zero dependencies |
| Deploy | Render + Vercel | Free tier friendly |

---

## Getting started

**Clone & install**
```bash
git clone https://github.com/prateek-1110/agentic-arxiv.git
cd agentic-arxiv/backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Add your key**
```bash
# backend/.env
GEMINI_API_KEY=your_gemini_api_key_here
```

**Run**
```bash
python main.py
# Backend  →  http://localhost:8000
# API docs →  http://localhost:8000/docs
```

**Open the frontend**

Open `frontend/index.html` with VS Code Live Server → `http://localhost:5500`

---

## API reference

| Method | Endpoint | |
|--------|----------|-|
| `POST` | `/ingest/pdf` | Upload a PDF |
| `POST` | `/ingest/arxiv` | Ingest by Arxiv ID or keyword |
| `GET` | `/ingest/list` | List ingested papers |
| `POST` | `/query/agent` | Agentic query with session memory |
| `POST` | `/query/` | Plain retrieval, no LLM |
| `POST` | `/query/session/new` | New session |
| `GET` | `/session/{id}` | Conversation history |
| `DELETE` | `/session/{id}` | Clear session |
| `GET` | `/health` | Health check |

---

## Design decisions worth noting

**No frameworks.** Retrieval, chunking, and agent logic are all written directly. Easier to debug, no version conflicts, no magic happening somewhere in a dependency chain.

**Lazy model loading.** Embedding model and reranker initialize on first request, not at startup. This keeps memory under Render's 512MB free-tier limit — a constraint that kills most deployed demos.

**Metadata-rich chunks.** Every chunk carries `arxiv_id`, `title`, `authors`, and `page_number`. Cited answers come for free, no post-processing needed.

**Duplicate-safe ingestion.** Papers are checked by `arxiv_id` before download. Chunks are checked by UUID before embedding. Call ingest multiple times without thinking about it.

---

## Project structure

```
agentic-arxiv/
├── backend/
│   ├── ingestion/
│   │   ├── pdf_loader.py          PDF parsing + chunking
│   │   ├── embedder.py            SentenceTransformer singleton
│   │   └── arxiv_fetcher.py       Arxiv API + PDF downloader
│   ├── retrieval/
│   │   ├── vectorstore.py         ChromaDB add / query / list
│   │   └── reranker.py            Cross-encoder reranking
│   ├── memory/
│   │   └── session_store.py       In-memory conversation history
│   ├── agent/
│   │   ├── agent_runner.py        Two-step LLM loop
│   │   ├── prompts.py             System prompts + templates
│   │   └── tools/
│   │       ├── vectorstore_tool.py
│   │       ├── arxiv_tool.py
│   │       └── summarize_tool.py
│   └── api/
│       └── routes/
│           ├── ingest.py          POST /ingest/*
│           ├── query.py           POST /query/*
│           └── session.py         GET | DELETE /session/*
└── frontend/
    ├── index.html
    ├── style.css
    └── app.js
```

---

<div align="center">
  Built by <b>Prateek Agrahari</b> • 
  <a href="https://www.linkedin.com/in/prateek1110/" target="_blank">
    <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/linkedin/linkedin-original.svg" 
         width="18" 
         height="18"
         alt="LinkedIn"
         style="vertical-align: middle;"/>
  </a>
</div>
