# SISUiQ Project Structure

> **Note**: This document reflects the actual implemented structure as of December 2024.

```
UETCL/
├── .claude/                                  # Claude AI project configuration
│   ├── config                               # Project context for AI assistance
│   ├── commands/                            # Custom commands
│   └── settings.local.json                  # Local settings
├── .gitignore                               # Git ignore rules
├── README.md                                # Project overview
├── STRUCTURE.md                             # This file
├── QUICKSTART.md                            # Quick setup guide
├── PROJECT_SETUP_SUMMARY.md                 # Setup summary & checklists
├── SECURITY_NOTES.md                        # Security considerations
├── package.json                             # Root package.json (MCP setup)
├── mcp-setup.sh                             # MCP setup script
│
├── frontend/                                 # Next.js Frontend Application
│   ├── app/                                 # Next.js App Router
│   │   ├── layout.tsx                       # Root layout
│   │   ├── page.tsx                         # Home page (chat interface)
│   │   ├── globals.css                      # Global styles
│   │   ├── admin/                           # Admin dashboard routes
│   │   │   ├── layout.tsx                   # Admin layout
│   │   │   ├── page.tsx                     # Admin home
│   │   │   ├── analytics/page.tsx           # Analytics page
│   │   │   ├── documents/page.tsx           # Documents page
│   │   │   └── sessions/page.tsx            # Sessions page
│   │   └── api/                             # Next.js API routes (proxy)
│   │       ├── chat/route.ts                # Chat endpoint proxy
│   │       ├── health/route.ts              # Health check
│   │       └── admin/                       # Admin API proxies
│   │           ├── analytics/route.ts
│   │           ├── documents/route.ts
│   │           ├── sessions/route.ts
│   │           └── stats/route.ts
│   ├── components/                          # React Components
│   │   ├── ui/                              # shadcn/ui base components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   ├── scroll-area.tsx
│   │   │   └── table.tsx
│   │   ├── chat/                            # Chat-specific components
│   │   │   ├── ChatBubble.tsx               # Message bubble component
│   │   │   └── ChatInput.tsx                # Input component
│   │   ├── admin/                           # Admin components (placeholder)
│   │   ├── analytics/                       # Analytics components (placeholder)
│   │   ├── InsightsPanel.tsx                # Insights sidebar
│   │   ├── Sidebar.tsx                      # Navigation sidebar
│   │   └── Topbar.tsx                       # Top navigation bar
│   ├── lib/                                 # Utilities & Helpers
│   │   └── utils.ts                         # Utility functions (cn helper)
│   ├── public/                              # Static Assets
│   │   └── assets/                          # Images, icons, fonts
│   ├── tests/                               # Frontend tests
│   │   └── copilot.spec.ts                  # Playwright test
│   ├── package.json                         # NPM dependencies
│   ├── tsconfig.json                        # TypeScript config
│   ├── tailwind.config.ts                   # Tailwind CSS config
│   ├── next.config.mjs                      # Next.js config
│   ├── postcss.config.mjs                   # PostCSS config
│   ├── playwright.config.ts                 # Playwright test config
│   ├── components.json                      # shadcn/ui config
│   ├── Dockerfile                           # Frontend Docker config
│   └── README.md                            # Frontend documentation
│
├── backend/                                  # FastAPI Backend Application
│   ├── main.py                              # Application entry point
│   ├── db.py                                # Database connection setup
│   ├── models.py                            # SQLAlchemy models (main)
│   ├── rag.py                               # RAG implementation (main)
│   ├── routers/                             # API Routers (FastAPI)
│   │   ├── __init__.py
│   │   ├── chat.py                          # Chat endpoints
│   │   ├── ingest.py                        # Ingestion endpoints
│   │   └── admin.py                         # Admin endpoints
│   ├── services/                            # Business Logic Services
│   │   ├── __init__.py
│   │   ├── chunking.py                      # Document chunking
│   │   ├── embeddings.py                    # Embedding generation
│   │   ├── llm.py                           # LLM integration
│   │   └── qdrant.py                        # Qdrant vector store
│   ├── api/                                 # API Layer (placeholder)
│   │   └── routes/                          # Future route expansion
│   ├── agents/                              # Agent System (placeholder)
│   ├── rag/                                 # RAG System (placeholder)
│   ├── models/                              # Data Models (placeholder)
│   ├── config/                              # Configuration (placeholder)
│   ├── utils/                               # Utilities (placeholder)
│   ├── storage/                             # Local storage
│   │   ├── data/                            # Data files
│   │   └── docs/                            # Document storage
│   ├── alembic/                             # Database migrations
│   │   ├── env.py                           # Alembic environment
│   │   ├── script.py.mako                   # Migration template
│   │   └── versions/                        # Migration files
│   │       └── 20241217_000001_001_initial_schema.py
│   ├── alembic.ini                          # Alembic configuration
│   ├── requirements.txt                     # Python dependencies
│   ├── Dockerfile                           # Backend Docker config
│   ├── .env.example                         # Environment template
│   └── README.md                            # Backend documentation
│
├── data/                                     # Data Storage
│   ├── strategy/                            # UETCL strategy PDFs
│   ├── era/                                 # ERA regulatory documents
│   ├── analytics/                           # Outage CSV & analytics data
│   └── README.md                            # Data documentation
│
├── docs/                                     # Documentation
│   ├── api/                                 # API Documentation
│   │   └── README.md                        # API reference
│   ├── architecture/                        # Architecture Docs
│   │   └── README.md                        # System architecture
│   ├── design/                              # Design System
│   │   ├── README.md                        # Design overview
│   │   ├── color-palette-skill.md           # Color system
│   │   └── figma-blueprint.md               # Figma specs
│   ├── DESIGN_QUICK_REFERENCE.md            # Quick design reference
│   ├── DESIGN_SYSTEM.md                     # Design system docs
│   └── FIGMA_BLUEPRINT.md                   # Figma blueprint
│
├── infra/                                    # Infrastructure
│   └── docker-compose.yml                   # Docker Compose orchestration
│
├── scripts/                                  # Utility Scripts
│   ├── setup/                               # Setup scripts (placeholder)
│   └── ingest/                              # Ingestion scripts (placeholder)
│
└── tests/                                    # Test Suites
    ├── frontend/                            # Frontend tests (placeholder)
    └── backend/                             # Backend tests (placeholder)
```

## Key Directories Explained

### Frontend (`/frontend`)
Next.js 15 application with TypeScript, shadcn/ui, and Tailwind CSS. Contains all UI components, pages, and client-side logic. Uses App Router with API route proxies to the backend.

### Backend (`/backend`)
FastAPI Python application. Contains the RAG system, routers for API endpoints, and business logic services. Uses Alembic for database migrations.

**Current Implementation:**
- `routers/` - FastAPI routers (chat, admin, ingest)
- `services/` - Core services (embeddings, LLM, Qdrant, chunking)
- `main.py` - Application entry point
- `db.py` - Database connection
- `models.py` - SQLAlchemy models
- `rag.py` - RAG implementation

**Placeholder directories** (for future expansion):
- `agents/` - Multi-mode agent system
- `rag/` - Extended RAG modules
- `models/` - Additional data models
- `config/` - Configuration modules
- `utils/` - Utility functions

### Infrastructure (`/infra`)
Docker Compose configuration for running all services together.

### Data (`/data`)
Storage for documents and datasets. Excluded from git for security.

### Docs (`/docs`)
Comprehensive documentation for architecture, API, deployment, and design system.

### Scripts (`/scripts`)
Automation scripts for setup and data ingestion (placeholders for future scripts).

### Tests (`/tests`)
Test suites for both frontend and backend (structure in place, tests to be added).

## File Naming Conventions

### Python (Backend)
- `snake_case.py` for modules
- `PascalCase` for classes
- `snake_case` for functions and variables
- `UPPER_CASE` for constants

### TypeScript/React (Frontend)
- `PascalCase.tsx` for React components
- `camelCase.ts` for utilities
- `kebab-case.css` for stylesheets
- `PascalCase` for React components and interfaces
- `camelCase` for functions and variables

## Configuration Files

### Backend
- `requirements.txt` - Python dependencies
- `.env` / `.env.example` - Environment variables (not committed)
- `Dockerfile` - Docker container config
- `alembic.ini` - Database migration config

### Frontend
- `package.json` - NPM dependencies
- `.env.local` - Environment variables (not committed)
- `next.config.mjs` - Next.js configuration
- `tailwind.config.ts` - Tailwind CSS theme
- `tsconfig.json` - TypeScript configuration
- `components.json` - shadcn/ui configuration
- `postcss.config.mjs` - PostCSS configuration
- `playwright.config.ts` - E2E test configuration

### Infrastructure
- `infra/docker-compose.yml` - Docker Compose orchestration

## Adding New Features

### New API Endpoint
1. Create router in `backend/routers/`
2. Add to router imports in `main.py`
3. Create Pydantic schemas in `models.py` or dedicated file
4. Update `docs/api/README.md`
5. Add tests in `tests/backend/`

### New Agent Mode (Future)
1. Create agent file in `backend/agents/`
2. Extend base agent class
3. Register in agent controller
4. Add tests in `tests/backend/`
5. Update frontend mode selector

### New UI Component
1. Create component in `frontend/components/`
2. Use shadcn/ui primitives from `components/ui/`
3. Follow design system in `docs/design/`
4. Add to relevant page in `app/`
5. Write tests in `frontend/tests/`

### New Service
1. Create service file in `backend/services/`
2. Export from `services/__init__.py`
3. Import and use in routers
4. Add tests

---

## Current Implementation Status

### ✅ Implemented
- FastAPI backend with routers (chat, admin, ingest)
- Core services (embeddings, LLM, Qdrant, chunking)
- Database models and migrations (Alembic)
- Next.js frontend with App Router
- Admin dashboard pages (sessions, documents, analytics)
- Chat interface components
- shadcn/ui component library
- Docker Compose infrastructure
- Design system documentation

### 🔲 Placeholder (Future Expansion)
- Multi-mode agent system (`backend/agents/`)
- Extended RAG modules (`backend/rag/`)
- Setup scripts (`scripts/setup/`)
- Ingestion scripts (`scripts/ingest/`)
- Comprehensive test suites

## Next Steps

1. **Set up development environment**
   - Install Python 3.10+ and Node.js 18+
   - Set up PostgreSQL and Qdrant
   - Configure environment variables

2. **Initialize databases**
   - Run `python scripts/setup/init_db.py`
   - Run `python scripts/setup/init_qdrant.py`

3. **Ingest sample data**
   - Generate sample data: `python scripts/setup/generate_sample_data.py`
   - Or place real data in `data/` directories

4. **Start services**
   - Backend: `cd backend && uvicorn main:app --reload`
   - Frontend: `cd frontend && npm run dev`

5. **Access application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
