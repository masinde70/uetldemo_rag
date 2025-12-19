# Implement Tasks 22-35: Enterprise Features

Execute the implementation plan for SISUiQ enterprise features in priority order.

## Usage

```bash
# Run all tasks in order
/implement-tasks-22-35

# Or implement specific phases by adding context
```

## Overview

Implementing 14 tasks across 6 phases:

| Phase | Tasks | Focus |
|-------|-------|-------|
| 1 | 25, 29 | Foundation (DevEx, CI/CD) |
| 2 | 23, 30 | Core Features (Prompts, Streaming) |
| 3 | 34, 28 | Reliability (Degraded Mode, Evaluation) |
| 4 | 22, 24 | Architecture (Agents, API Versioning) |
| 5 | 26, 27, 32 | Testing (Load, Visual, Citations) |
| 6 | 33, 31, 35 | Enterprise (Jobs, Multi-Tenant, Roadmap) |

---

## Phase 1: Foundation

### Task 25 - Developer Experience

**Extend Makefile** with targets:

- `install` - Install all dependencies
- `dev` / `dev-backend` / `dev-frontend` - Development servers
- `lint` / `format` - Code quality
- `test` / `test-e2e` - Testing
- `seed` / `migrate` - Database
- `pre-commit-install` - Git hooks

**Create `.pre-commit-config.yaml`** with:

- Ruff (Python linting/formatting)
- mypy (Python type checking)
- Prettier/ESLint (Frontend)
- Standard pre-commit hooks

**Create `pyproject.toml`** with tool configuration.

### Task 29 - CI/CD Pipeline

**Create `.github/workflows/`**:

- `ci.yml` - Lint + test on push/PR
- `cd-staging.yml` - Deploy to staging on main branch
- `cd-prod.yml` - Deploy to prod on release tags

**Use GitHub Container Registry (GHCR)** for images.

**Create `docs/DEPLOYMENT.md`**.

---

## Phase 2: Core Features

### Task 23 - System Prompt Templates

**Create `backend/prompts/`**:

- `templates.py` - BASE_PERSONA, MODE_TEMPLATES
- `builder.py` - build_system_prompt(), build_context()

**Migrate** inline prompts from `backend/services/llm.py`.

**Create `docs/PROMPTING.md`**.

### Task 30 - Streaming Responses

**Backend**:

- `backend/routers/chat_stream.py` - SSE endpoint
- `backend/services/llm_stream.py` - Token streaming generator
- Add `sse-starlette==1.8.2` dependency

**Frontend**:

- `frontend/lib/hooks/useStreamingChat.ts` - React hook
- `frontend/app/api/chat/stream/route.ts` - Proxy route
- Update `frontend/app/page.tsx` for streaming UI

**Create `docs/STREAMING.md`**.

---

## Phase 3: Reliability

### Task 34 - Offline/Degraded Mode

**Backend**:

- `backend/services/health.py` - Service health checking
- Add `degraded: bool` to ChatResponse
- Fallback responses when services unavailable

**Frontend**:

- `frontend/components/ui/DegradedBanner.tsx` - Warning banner
- Show banner when response.degraded is true

**Create `docs/DEGRADED_MODE.md`**.

### Task 28 - LLM Evaluation

**Create**:

- `eval/questions.json` - Test dataset
- `backend/scripts/eval_rag.py` - Evaluation script

**Metrics**: source_recall, latency_ms, topic coverage.

**Create `docs/EVALUATION.md`**.

---

## Phase 4: Architecture

### Task 22 - Multi-Agent Architecture

**Create `backend/agents/`**:

- `base.py` - BaseAgent ABC, AgentContext, AgentResponse
- `orchestrator.py` - Mode-to-agent routing
- `strategy_agent.py` - Strategy specialist
- `analytics_agent.py` - Analytics specialist
- `regulatory_agent.py` - Regulatory specialist

**Update**:

- `backend/main.py` - Register agents in lifespan
- `backend/routers/chat.py` - Use orchestrator

**Create `tests/backend/test_orchestrator.py`**.

### Task 24 - API Versioning

**Create `backend/routers/v1/`**:

- Versioned copies of chat, admin, ingest routers
- Maintain backward compatibility with legacy routes

**Add OpenAPI examples** to Pydantic models.

**Create `docs/API.md`**.

---

## Phase 5: Testing

### Task 26 - Load Testing (k6)

**Create `loadtest/`**:

- `config.js` - Shared configuration
- `chat_test.js` - Chat endpoint test
- `admin_test.js` - Admin endpoint test
- `login_test.js` - Auth flow test

**Create `docs/LOADTEST.md`**.

### Task 27 - UI Regression Tests

**Create `tests/visual/`**:

- `home.spec.ts` - Homepage screenshots
- `admin.spec.ts` - Admin screenshots
- `mobile.spec.ts` - Mobile viewport tests

**Update `playwright.config.ts`** for snapshots.

**Create `docs/REGRESSION_TESTS.md`**.

### Task 32 - Document Lineage

**Create `frontend/components/SourceCard.tsx`** with copy button.

**Enhance citations** in backend to include page, snippet, document_id.

**Create `docs/CITATIONS.md`**.

---

## Phase 6: Enterprise

### Task 33 - Scheduled Analytics Jobs

**Create `backend/jobs/`**:

- `scheduler.py` - APScheduler setup
- `analytics_refresh.py` - Nightly KPI refresh
- `cleanup.py` - Session cleanup

**Add `APScheduler==3.10.4`** dependency.

**Create `docs/JOBS.md`**.

### Task 31 - Multi-Tenant Support

**Create migration** adding:

- `tenants` table
- `tenant_id` FK to relevant tables

**Create `backend/middleware/tenant.py`**.

**Add Qdrant payload filtering** by tenant_id.

**Create `docs/MULTI_TENANCY.md`**.

### Task 35 - Enterprise Extension Plan

**Create `docs/ENTERPRISE_ROADMAP.md`** covering:

- RBAC
- Audit logs
- Compliance exports
- SLA metrics
- Model governance
- Retention policies

---

## Validation Checklist

After each task:

- [ ] Code follows existing patterns (async functions, env config, UUID PKs)
- [ ] Tests pass (`make test && make test-e2e`)
- [ ] Linting passes (`make lint`)
- [ ] Documentation created
- [ ] No breaking changes to existing API

---

## Dependencies to Add

**backend/requirements.txt**:

```text
sse-starlette==1.8.2
APScheduler==3.10.4
ruff==0.1.9
mypy==1.8.0
pytest-asyncio==0.23.3
```

---

## User Preferences

- **Scope**: All 14 tasks (including enterprise features)
- **Container Registry**: GitHub Container Registry (GHCR)
- **Streaming**: Token-by-token streaming (real-time like ChatGPT)
