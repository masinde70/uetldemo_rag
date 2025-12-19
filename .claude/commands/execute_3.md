# Tasks
Read .claude/config
The continue to the tasks
# TASK 9 Seed Database With Demo Data
You are a backend and database engineer.
Project: “SISUiQ – ERA/UETCL Strategy & Regulatory Copilot” (FastAPI + Postgres + Qdrant).

Use Sequential Thinking first to outline:
- what data you will seed
- how to avoid duplicates
- how to run automatically in dev only

Task:
Write backend/seed.py that seeds PostgreSQL with demo data.

Seed:
1) Demo user
- email: demo@sisuiq.com
- name: “Demo Admin”
- role: admin

2) Three chat sessions for that user
- modes: strategy_qa, regulatory, analytics
- each session has 2–3 user messages + 2–3 assistant messages (timestamps realistic)

3) Analytics snapshot
- dataset_name: “demo_outages”
- payload (JSONB) with example outage KPIs:
  - total_events
  - total_customers_affected
  - saifi
  - saidi
  - top_regions (array)
  - note (string)

4) Document metadata
- strategic_plan.pdf (source: UETCL, type: strategy)
- grid_development_plan.pdf (source: UETCL, type: strategy)
(Only metadata rows; chunks/embeddings not required in this seed.)

Requirements:
- Must work with the project’s SQLAlchemy setup (if the app uses AsyncSession, seed.py must also be async; keep consistency).
- Ensure tables exist before seeding:
  - run Alembic migrations if present OR fallback to Base.metadata.create_all (choose one; prefer Alembic if configured).
- Implement a reusable get_or_create helper to prevent duplicate records.
- Print a clean summary at the end: created vs already existed counts.

Docker Compose requirement:
- Modify infra/docker-compose.yml so seeding runs automatically ONLY in dev.
- Use one of these approaches (pick one and implement cleanly):
  A) A separate “seed” one-shot service enabled via Compose profiles (preferred).
  B) Backend entrypoint runs seed only when RUN_SEED=true.
- The seed must NOT run in staging/prod unless manually invoked.

Deliverables:
- full backend/seed.py
- docker-compose.yml updates (and/or docker-compose.dev.yml if you choose overrides)
- README snippet showing:
  - automatic dev seeding
  - manual run: docker compose exec backend python -m backend.seed (or equivalent)


# TASK 10 Admin Dashboard API
You are a backend engineer.
Project: SISUiQ Copilot (FastAPI + SQLAlchemy).

Use Sequential Thinking to outline:
- endpoint list
- auth guard
- pagination pattern
- query optimizations (selectinload)

Task:
Create an admin-only API router for reviewing demo data.

Endpoints:
- GET /api/admin/users
- GET /api/admin/sessions
- GET /api/admin/sessions/{id}/messages
- GET /api/admin/analytics
- GET /api/admin/documents

Functional requirements:
- Use Depends(get_current_user).
- Access allowed only if current_user.role == "admin".
- Pagination on list endpoints: limit, offset.
- Use SQLAlchemy ORM query patterns.
- Use .options(selectinload(...)) where it prevents N+1 queries.
- Return consistent JSON envelopes:
  { "data": [...], "count": <int> }

Output requirements:
- Full router implementation: backend/routers/admin.py
- Example JSON responses for each endpoint (short and realistic)
- Instructions to include router in backend/main.py (prefix="/api")

Keep everything clean, minimal, and consistent with existing models.

# TASK 11 Minimal Admin UI (Next.js + shadcn/ui)

You are a senior frontend engineer using Next.js 14 (App Router), TypeScript, Tailwind, and shadcn/ui.
UI style: minimal, white background, blue primary, red accent.

Use Sequential Thinking to outline:
- routing structure under /admin
- shared layout components
- data fetching helper with auth
- table + detail views

Task:
Build a minimal admin dashboard under /admin with pages:
- /admin/users
- /admin/sessions
- /admin/sessions/[id]
- /admin/analytics
- /admin/documents

Visual requirements:
- Background: #FFFFFF
- Primary (ERA Blue): #0033A0
- Accent (ERA Red): #ED1C24 (only for warnings/badges)
- Simple typography, lots of whitespace, 1px borders (slate-200)

Components to use (shadcn/ui):
- Card, Table, Button, ScrollArea, Input, Badge

Functional requirements:
- Assume JWT token stored in localStorage under key: "token"
- Create frontend/lib/api.ts helper:
  - apiGet(path), apiPost(path)
  - includes Authorization: Bearer <token>
  - handles errors and returns typed results
- Create reusable layout:
  components/AdminLayout.tsx
  - Sidebar (fixed)
  - Topbar (light)
  - Main content (scrollable)

UI requirements:
- Sessions page: table with session id, mode, title, created_at, user email
- Session detail page: message viewer UI (user vs assistant bubbles, minimal)
- Documents page: table with name, type, source, created_at
- Analytics page: list snapshots with dataset_name, created_at, key KPIs
- Users page: table with email, name, role, created_at

Output requirements:
- Full code for:
  - components/AdminLayout.tsx
  - each admin page (5 pages)
  - session message viewer component
  - frontend/lib/api.ts
- Example API calls (fetch via api.ts), wired to backend endpoints

Keep it minimal and consistent with the main app styling.


# TASK 12 Logging, Tracing & Metrics
You are an observability engineer for a FastAPI backend.

Use Sequential Thinking to outline:
- logging format + context
- trace_id generation + propagation
- metrics naming + where to increment
- minimal dev Prometheus setup

Task:
Add structured logging, tracing, and basic metrics to the FastAPI backend.

Logging:
- Use structlog
- JSON logs
- Middleware:
  - request start/end logs (method, path, status, duration_ms)
  - exception logging (stack trace)
  - chat lifecycle logs: rag_ms, llm_ms, analytics_ms (when relevant)
- Ensure logs include:
  - trace_id
  - user_id (if available)
  - session_id (for /api/chat)
  - mode (for /api/chat)

Tracing:
- Each incoming request gets a trace_id:
  - accept X-Trace-Id if present, otherwise generate UUID
- Attach trace_id to:
  - response header X-Trace-Id
  - all log entries
- (Optional but preferred) Add OpenTelemetry FastAPI instrumentation with OTLP exporter:
  - enabled only if OTEL_EXPORTER_OTLP_ENDPOINT is set
  - otherwise no-op

Metrics:
- Expose GET /metrics in Prometheus text format
- Counters:
  - chat_requests_total
  - rag_queries_total
  - analytics_runs_total
- Histograms (minimal):
  - rag_duration_seconds
  - llm_duration_seconds
  - request_duration_seconds

Docker Compose:
- Add an optional Prometheus service for dev only (profiles: ["dev"]).
- Provide prometheus.yml scrape config to scrape backend:8000/metrics.

Deliverables:
- middleware + logging setup modules (backend/observability/* or similar)
- updated FastAPI app registration (backend/main.py)
- prometheus.yml
- example JSON log lines (short)


# TASK 13 Deployment Hardening via Nginx Reverse Proxy
You are a DevOps and security engineer.
We are containerizing a Next.js frontend and FastAPI backend.

Use Sequential Thinking to outline:
- routing rules
- security headers
- upload/timeouts for LLM + PDFs
- compose network exposure rules
- TLS approach for staging/prod

Task:
Add an Nginx reverse proxy layer in Docker.

Routing:
- /api/* -> backend (FastAPI)
- /* -> frontend (Next.js)

Security headers (add to ALL responses):
- Content-Security-Policy (reasonable default; allow self; allow inline styles only if needed)
- X-Frame-Options: DENY
- Referrer-Policy: no-referrer
- Strict-Transport-Security (for TLS deployments; safe defaults)
- X-Content-Type-Options: nosniff

LLM/file optimizations:
- client_max_body_size 20M;
- proxy_read_timeout 300s;
- proxy_send_timeout 300s;

Requirements:
- Provide full nginx.conf
- Update docker-compose.yml:
  - expose ONLY Nginx publicly (80; optionally 443 for staging/prod)
  - frontend, backend, postgres, qdrant should be internal only
- Include simple instructions for enabling TLS in staging/prod:
  - self-signed certs example (paths mounted)
  - how to switch Nginx to listen 443 and redirect 80->443

Deliverables:
- infra/nginx/nginx.conf
- docker-compose.yml updates
- short README notes for TLS enablement
Keep configuration minimal and clear.


# TASK 14 Production Checklist
You are a senior DevOps lead.

Task:
Produce a production-readiness checklist for the “SISUiQ – ERA/UETCL Strategy & Regulatory Copilot”.

Style:
- Minimal, structured Markdown
- ERA branding vibe: clean headings, no fluff

Sections (must include all):
- Infrastructure
- Network & Proxy
- Backend Service
- Frontend
- PostgreSQL Database
- Qdrant Vector Store
- Observability
- Security

Levels:
- MUST
- SHOULD
- OPTIONAL

Must include at minimum:
- Dependency pinning
- Container hardening (non-root, slim images, read-only FS where possible)
- Secret management strategy (env, vault/KMS, CI secrets)
- TLS details (termination at proxy, cert rotation)
- Rate limits (especially /api/chat)
- Backups (Postgres + Qdrant) and restore testing
- Key rotation (API keys)
- CORS configuration (locked to frontend origin)
- Upload limits + file scanning considerations

Deliverable:
- SECURITY_NOTES.md or PRODUCTION_CHECKLIST.md (pick one and be consistent with earlier docs)
