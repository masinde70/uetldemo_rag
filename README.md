# SISUiQ – UETCL Strategy, Regulatory & Service Copilot

> **Unified AI Knowledge & Decision Layer for Utilities**

A full-stack AI copilot demo showcasing hybrid RAG, agentic reasoning, and regulatory intelligence for Uganda Electricity Transmission Company Ltd (UETCL).

## Quick Start (Docker)

The fastest way to get started:

```bash
# Clone and start all services
cd infra
docker compose up --build

# Visit http://localhost:3000
```

This starts:
- **Frontend** at http://localhost:3000
- **Backend** (internal only, accessed via frontend proxy)
- **PostgreSQL** (internal)
- **Qdrant** (internal)

## Local Development

### Prerequisites
- Python 3.13+ (or 3.11+)
- Node.js 20+ LTS
- Docker (for PostgreSQL & Qdrant)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

### Start Databases (Docker)
```bash
# PostgreSQL
docker run -d --name sisuiq-postgres \
  -e POSTGRES_USER=sisuiq \
  -e POSTGRES_PASSWORD=sisuiq \
  -e POSTGRES_DB=sisuiq \
  -p 5432:5432 postgres:16-alpine

# Qdrant
docker run -d --name sisuiq-qdrant \
  -p 6333:6333 qdrant/qdrant
```

## Project Structure

```
UETCL/
├── frontend/          # Next.js 15 + TypeScript + Tailwind + shadcn/ui
├── backend/           # FastAPI (Python)
├── infra/             # Docker Compose orchestration
├── data/              # Strategy docs, ERA content, analytics
├── docs/              # Documentation
├── scripts/           # Setup and ingestion scripts
└── tests/             # Test suites
```

## Core Features

### 1. Strategy Copilot
- Query UETCL's 2024–2029 Strategic Plan
- Extract objectives, KPIs, and initiatives
- Get citation-backed answers

### 2. Regulatory Intelligence (ERA)
- Compliance Q&A
- Regulatory checklists
- Map UETCL goals to ERA requirements

### 3. Analytics + Strategy Fusion
- Outage data analysis
- Combine analytics with strategic goals
- Data-driven recommendations

### 4. Admin Dashboard
- Monitor sessions and usage
- View ingested documents
- Analytics snapshots

## Technical Highlights

- **Hybrid RAG**: Semantic (Qdrant) + Keyword (Postgres FTS) + RRF Fusion
- **Multi-Mode Agents**: Strategy Q&A, Action Planner, Analytics, Regulatory Advisor
- **Modern Stack**: Next.js 15, FastAPI, shadcn/ui, Tailwind CSS
- **AI Models**: GPT-4.1, text-embedding-3-small

## Design

**ERA-inspired minimal theme** - Clean, professional UI with white background, blue primary, and red accent colors. Designed for enterprise demos with consultants, executives, and regulators.

## Documentation

- [Architecture Overview](docs/architecture/README.md)
- [API Documentation](docs/api/README.md)
- [Design System](docs/design/README.md)

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/version` | GET | Version info |

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://sisuiq:sisuiq@localhost:5432/sisuiq
QDRANT_HOST=localhost
QDRANT_PORT=6333
CORS_ORIGINS=http://localhost:3000
ENVIRONMENT=development
```

### Frontend (.env.local)
```
BACKEND_URL=http://localhost:8000
```

## License

Proprietary - SISUiQ Demo Project

## Support

For questions or issues, contact the development team.
