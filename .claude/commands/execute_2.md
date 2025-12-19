# Execute Command
read the content of
.claude/config
# Task 6 Admin dashboard (sessions, docs, analytics)
Task: Build a simple admin dashboard.

Backend:
- Admin endpoints under /api/admin/*
- Require admin user (demo stub ok):
  - e.g. X-Admin-Token header equals env ADMIN_TOKEN
  - clearly marked as demo-only in code + SECURITY_NOTES.md
Endpoints:
- GET /api/admin/sessions (id, user, mode, created_at)
- GET /api/admin/sessions/{id}/messages
- GET /api/admin/documents
- GET /api/admin/analytics

Frontend:
- /admin layout with left nav:
  - Sessions
  - Documents
  - Analytics
- Table views using shadcn/ui Table
- Same visual language: white, gray borders, blue links, red only for warnings/deletes

Deliverables:
- backend/routers/admin.py
- frontend/app/admin/* pages
- shared types in frontend for responses

# Task 7 Playwright E2E tests for key flows
Task: Add Playwright e2e tests for key flows.

Flows:
1) User opens home:
- sees sidebar items
- sees chat input
- sees insights panel

2) User sends a question:
- types into input
- clicks send
- receives at least one assistant message rendered

3) Admin visits /admin:
- sees sessions list populated after chat

Testing strategy:
- Choose one:
  A) Spin up full stack with docker-compose in CI and run Playwright against http://localhost:3000
  B) For demo simplicity, mock Next.js /api/chat route in test environment to return canned response, but still create a session via backend is preferred.
- Document which approach you picked and why.

Implementation:
- Use stable selectors:
  - data-testid for chat input, send button, message list, sidebar, insights, admin table
- Keep tests minimal and non-brittle.

Deliverables:
- playwright.config.ts
- tests/copilot.spec.ts
- npm scripts: test:e2e


# Task 8 Security + deployment hardening checklist
Task: Review infra and app code for basic security & deployment readiness, then produce concrete improvements.

Cover:
- Docker images: slim base, non-root where possible
- Network: only publish frontend; backend/db/qdrant internal
- Secrets: env vars; .env.example; never commit keys
- CORS: lock backend to frontend origin(s)
- Rate limiting: basic protection on /api/chat
- Logging: structured logs; avoid leaking sensitive doc text
- File uploads: size limits; content-type checks; store outside repo
- Dependency hygiene: pin versions; minimal packages

Deliverable:
- SECURITY_NOTES.md including:
  - “demo-grade only” disclaimer
  - what to fix before production
  - concrete changes (compose, Dockerfiles, FastAPI middleware, headers)

