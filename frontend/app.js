const API = "http://localhost:8000";

let sessionId = null;

// ── DOM refs ───────────────────────────────────────────────
const chatMessages   = document.getElementById("chatMessages");
const queryInput     = document.getElementById("queryInput");
const sendBtn        = document.getElementById("sendBtn");
const arxivInput     = document.getElementById("arxivInput");
const ingestArxivBtn = document.getElementById("ingestArxivBtn");
const pdfInput       = document.getElementById("pdfInput");
const uploadZone     = document.getElementById("uploadZone");
const uploadLabel    = document.getElementById("uploadLabel");
const uploadBtn      = document.getElementById("uploadBtn");
const paperList      = document.getElementById("paperList");
const refreshListBtn = document.getElementById("refreshListBtn");
const newSessionBtn  = document.getElementById("newSessionBtn");
const sessionDisplay = document.getElementById("sessionDisplay");
const statusDot      = document.getElementById("statusDot");
const toast          = document.getElementById("toast");

// ── Init ───────────────────────────────────────────────────
(async function init() {
  await checkHealth();
  await startNewSession();
  await refreshPaperList();
})();

// ── Health check ───────────────────────────────────────────
async function checkHealth() {
  try {
    const res = await fetch(`${API}/health`);
    if (res.ok) {
      statusDot.classList.add("online");
    } else {
      statusDot.classList.add("offline");
    }
  } catch {
    statusDot.classList.add("offline");
  }
}

// ── Session ────────────────────────────────────────────────
async function startNewSession() {
  try {
    const res  = await fetch(`${API}/query/session/new`, { method: "POST" });
    const data = await res.json();
    sessionId  = data.session_id;
    sessionDisplay.textContent = sessionId.slice(0, 8) + "…";
    clearChat();
  } catch {
    showToast("Could not create session.", "error");
  }
}

newSessionBtn.addEventListener("click", async () => {
  await startNewSession();
  showToast("New session started.", "success");
});

// ── Ingest Arxiv ───────────────────────────────────────────
ingestArxivBtn.addEventListener("click", async () => {
  const query = arxivInput.value.trim();
  if (!query) return;

  ingestArxivBtn.disabled = true;
  ingestArxivBtn.textContent = "…";

  try {
    const res  = await fetch(`${API}/ingest/arxiv`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ arxiv_id_or_query: query }),
    });
    const data = await res.json();

    if (!res.ok) {
      showToast(data.detail || "Ingest failed.", "error");
      return;
    }

    const msg = data.status === "already_ingested"
      ? `Already ingested: ${data.title}`
      : `Ingested: ${data.title} (${data.chunks_added} chunks)`;

    showToast(msg, "success");
    arxivInput.value = "";
    await refreshPaperList();
  } catch {
    showToast("Network error during ingest.", "error");
  } finally {
    ingestArxivBtn.disabled = false;
    ingestArxivBtn.textContent = "Fetch";
  }
});

// ── Upload PDF ─────────────────────────────────────────────
pdfInput.addEventListener("change", () => {
  if (pdfInput.files[0]) {
    uploadLabel.textContent = pdfInput.files[0].name;
    uploadZone.classList.add("has-file");
  }
});

uploadBtn.addEventListener("click", async () => {
  const file = pdfInput.files[0];
  if (!file) { showToast("Select a PDF first.", "error"); return; }

  uploadBtn.disabled = true;
  uploadBtn.textContent = "Uploading…";

  const form = new FormData();
  form.append("file", file);

  try {
    const res  = await fetch(`${API}/ingest/pdf`, { method: "POST", body: form });
    const data = await res.json();

    if (!res.ok) {
      showToast(data.detail || "Upload failed.", "error");
      return;
    }

    showToast(`Uploaded: ${data.filename} (${data.chunks_added} chunks)`, "success");
    pdfInput.value  = "";
    uploadLabel.textContent = "Drop PDF or click";
    uploadZone.classList.remove("has-file");
    await refreshPaperList();
  } catch {
    showToast("Network error during upload.", "error");
  } finally {
    uploadBtn.disabled = false;
    uploadBtn.textContent = "Upload";
  }
});

// ── Paper list ─────────────────────────────────────────────
async function refreshPaperList() {
  try {
    const res   = await fetch(`${API}/ingest/list`);
    const data  = await res.json();
    const papers = data.papers || [];

    if (papers.length === 0) {
      paperList.innerHTML = `<span class="empty-hint">None yet.</span>`;
      return;
    }

    paperList.innerHTML = papers.map(p => `
      <div class="paper-item">
        <div class="paper-item-title">${p.title || p.source || "Untitled"}</div>
        ${p.arxiv_id ? `<div class="paper-item-id">${p.arxiv_id}</div>` : ""}
      </div>
    `).join("");
  } catch {
    paperList.innerHTML = `<span class="empty-hint">Could not load.</span>`;
  }
}

refreshListBtn.addEventListener("click", refreshPaperList);

// ── Chat ───────────────────────────────────────────────────
sendBtn.addEventListener("click", sendQuery);

queryInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendQuery();
  }
});

queryInput.addEventListener("input", () => {
  queryInput.style.height = "auto";
  queryInput.style.height = Math.min(queryInput.scrollHeight, 160) + "px";
});

async function sendQuery() {
  const question = queryInput.value.trim();
  if (!question || !sessionId) return;

  appendMessage("user", question);
  queryInput.value = "";
  queryInput.style.height = "auto";

  const thinkingEl = appendThinking();
  sendBtn.disabled = true;

  try {
    const res  = await fetch(`${API}/query/agent`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ question, session_id: sessionId }),
    });
    const data = await res.json();

    thinkingEl.remove();

    if (!res.ok) {
      appendMessage("assistant", `Error: ${data.detail || "Something went wrong."}`);
      return;
    }

    appendMessage("assistant", data.answer, data.sources, data.tool_used);
  } catch {
    thinkingEl.remove();
    appendMessage("assistant", "Network error. Is the backend running?");
  } finally {
    sendBtn.disabled = false;
    scrollToBottom();
  }
}

// ── Message rendering ──────────────────────────────────────
function appendMessage(role, text, sources = [], toolUsed = null) {
  const welcome = chatMessages.querySelector(".welcome-msg");
  if (welcome) welcome.remove();

  const el = document.createElement("div");
  el.className = `message ${role}`;

  const roleLabel = role === "user" ? "YOU" : "ARXIV/RAG";

  let sourcesHTML = "";
  if (sources && sources.length > 0) {
    const chips = sources.map(s => {
      const label = s.title
        ? s.title.length > 40 ? s.title.slice(0, 40) + "…" : s.title
        : s.arxiv_id || s.source || "source";
      const page  = s.page_number ? ` · p${s.page_number}` : "";
      return `<span class="source-chip">${label}${page}</span>`;
    }).join("");
    sourcesHTML = `<div class="message-sources">${chips}</div>`;
  }

  const toolHTML = toolUsed
    ? `<div class="tool-badge">via ${toolUsed}</div>`
    : "";

  el.innerHTML = `
    <div class="message-role">${roleLabel}</div>
    <div class="message-body">${escapeHTML(text)}</div>
    ${sourcesHTML}
    ${toolHTML}
  `;

  chatMessages.appendChild(el);
  scrollToBottom();
}

function appendThinking() {
  const el = document.createElement("div");
  el.className = "thinking";
  el.innerHTML = `thinking <span class="thinking-dots"><span>.</span><span>.</span><span>.</span></span>`;
  chatMessages.appendChild(el);
  scrollToBottom();
  return el;
}

function clearChat() {
  chatMessages.innerHTML = `
    <div class="welcome-msg">
      <p class="welcome-title">Ask anything about your papers.</p>
      <p class="welcome-sub">Ingest an Arxiv paper or upload a PDF, then start chatting.</p>
    </div>
  `;
}

// ── Utilities ──────────────────────────────────────────────
function scrollToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHTML(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

let toastTimer;
function showToast(msg, type = "") {
  toast.textContent = msg;
  toast.className   = `toast ${type} show`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.classList.remove("show");
  }, 3200);
}