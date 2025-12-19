# Execute Command
# Task 2 Design DB schema & SQLAlchemy models
Task: Design the PostgreSQL schema + SQLAlchemy models.

Entities:

users:
- id (UUID, pk)
- email (unique)
- name
- role (admin|user)
- created_at

chat_sessions:
- id (UUID, pk)
- user_id (FK users.id)
- title
- mode (strategy_qa | actions | analytics | regulatory)
- created_at

chat_messages:
- id (UUID, pk)
- session_id (FK chat_sessions.id)
- role (user | assistant)
- content (text)
- created_at

documents:
- id (UUID, pk)
- name
- type (strategy | regulation | other)
- source (UETCL | ERA | other)
- file_path
- created_at

analytics_snapshots:
- id (UUID, pk)
- dataset_name
- payload (JSONB)
- created_at

document_chunks:
- id (UUID, pk)
- document_id (FK documents.id)
- chunk_index (int)
- text (text)
- source (short string; e.g. “UETCL Strategic Plan 2024–2029”)
- page (int, nullable)
- fts_vector (tsvector, generated/maintained for FTS)

Requirements:
- Use Sequential Thinking to design relationships and indexes.
- Use SQLAlchemy 2.0 style with Async (asyncpg) OR Sync—pick one and stick to it.
  - Preference: Async SQLAlchemy + asyncpg.
- Create backend/db.py with:
  - Async engine
  - Async session maker
  - Base
  - get_db dependency
- Provide migrations using Alembic:
  - alembic init
  - first revision that creates tables + indexes
  - FTS index (GIN) on document_chunks.fts_vector
- Ensure chunk text updates also update fts_vector (trigger or computed column).
  - Choose one approach and implement cleanly.

Deliverables:
- models.py
- db.py
- alembic/ configuration + first migration
- short notes in README on running migrations

# Task 3 Implement RAG ingestion & hybrid retrieval (RRF)
Task: Implement ingestion pipeline + hybrid retrieval using RRF.

Ingestion endpoints (FastAPI):
1) POST /api/ingest/docs
- Accepts PDF upload (multipart/form-data).
- Stores original file in backend storage folder (e.g. backend/storage/docs/{uuid}.pdf).
- Extracts text from PDF (use pypdf or pdfminer.six; keep it simple).
- Splits into chunks ~500–800 tokens with overlap (use tiktoken if available; otherwise approximate by words).
- Inserts a documents row and document_chunks rows.
- Embeds each chunk using OpenAI embeddings (env: OPENAI_API_KEY, OPENAI_EMBED_MODEL).
- Upserts embeddings into Qdrant collection (env: QDRANT_URL, QDRANT_COLLECTION).
- Store chunk_id, document_id, chunk_index, page (if available), source/title in Qdrant payload.

2) POST /api/ingest/data
- Accepts CSV upload (outage events).
- Stores raw file path in backend storage folder (backend/storage/data/{uuid}.csv).
- Creates analytics_snapshots entry with:
  - dataset_name
  - payload JSON summary (row count, date min/max if columns exist, simple counts by category if present).
- Keep this minimal and robust if columns vary.

Retrieval module (backend/rag.py):
- semantic_search(query: str, top_k: int) -> ranked hits (from Qdrant)
- keyword_search(query: str, top_k: int) -> ranked hits (Postgres FTS over document_chunks)
- rrf_fusion(semantic_hits, keyword_hits, k=60) merges ranked lists using Reciprocal Rank Fusion
- hybrid_retrieve(query: str, top_n: int=8) returns fused list of chunks with metadata:
  - text
  - source/title
  - document name
  - page
  - file reference

Implementation details:
- Add lightweight dedup (same chunk id) during fusion.
- Add optional filters parameter scaffold (source/type/year) even if not fully used yet.
- Use Context7/Serena to keep code organized: routers/ingest.py, rag.py, services/embeddings.py, services/qdrant.py.

Deliverables:
- Ingestion routers
- rag.py retrieval logic with tests (unit tests ok, keep minimal)
- Qdrant collection auto-create on startup (if missing)

# Task 4 Implement agent controller & /api/chat endpoint
Task: Implement agent logic + chat endpoint using hybrid RAG.

Modes:
- strategy_qa: focus UETCL strategy docs
- actions: convert insights into actionable steps
- analytics: combine outage analytics snapshot summaries + docs
- regulatory: focus ERA docs/regulations

Models:
ChatRequest:
- message: str
- mode: str
- session_id: Optional[str]

ChatResponse:
- answer: str
- session_id: str
- sources: List[str]
- analytics: Optional[dict]

/api/chat behavior:
- Resolve current user (demo auth is fine: e.g. X-User-Email header or hardcoded user in env).
- Find or create chat_session for this user:
  - if session_id provided, load it and verify ownership
  - else create new session with title derived from first message
- Store user message in chat_messages.
- Retrieve context using hybrid_retrieve(message) for most modes:
  - apply source/type filter based on mode:
    - strategy_qa/actions/analytics -> prefer source=UETCL
    - regulatory -> prefer source=ERA
- For analytics mode:
  - load latest analytics_snapshot (or by dataset_name if provided later)
  - include a compact summary object for the prompt + return it in response.analytics
- Build a minimal system prompt:
  - serious, regulator/utility consultant tone
  - use only provided context
  - cite sources like [UETCL Strategic Plan p.12] or [ERA Regulation XYZ]
  - if insufficient context, say so and propose what doc is needed
- Call OpenAI chat completion (env: OPENAI_API_KEY, OPENAI_CHAT_MODEL).
- Store assistant message in chat_messages.
- Return ChatResponse with sources list (unique, ordered) and analytics payload if any.

Deliverables:
- routers/chat.py
- services/llm.py
- prompt builder helpers
- DB write/read helpers for sessions/messages

# Task 5 Implement minimalistic ERA-style UI (Next.js + shadcn/ui)
Task: Build the main Copilot interface in Next.js with minimal ERA-aligned design.

Visual:
- Background mostly white or very light gray
- Blue as primary (buttons/active states)
- Red sparingly (alerts/accent)
- 1px light gray borders, lots of whitespace, clean typography
- No gradients/neon/futuristic visuals

Layout:
- Topbar: title/mark left; user/avatar right
- Left sidebar: modes
  - Strategy Q&A
  - Action Planner
  - Analytics + Strategy
  - Regulatory Advisor
- Center: chat area (messages + input)
- Right panel: insights (sources, analytics highlights, recommendations)

Implementation:
- Use shadcn/ui Button, Card, Input, ScrollArea, Table (later)
- Use Tailwind classes: bg-white, text-slate-800, border-slate-200, text-blue-600, text-red-600
- Components:
  - Sidebar
  - Topbar
  - ChatBubble
  - ChatInput
  - InsightsPanel
- State:
  - selected mode
  - session_id persisted (localStorage ok for demo)
  - messages list
- API:
  - call same-origin Next.js route handler /api/chat that proxies to backend (preferred)
  - stream optional later; for now simple request/response

Deliverables:
- app/page.tsx as main shell
- components/* extracted cleanly
- minimal design tokens in globals.css (optional)

if done continue to the file excute_2.md