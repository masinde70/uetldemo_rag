# SISUiQ Backend

FastAPI backend with hybrid RAG, multi-mode agents, and analytics engine.

## 📁 Structure

```
backend/
├── api/
│   ├── routes/           # API endpoint definitions
│   │   ├── chat.py      # Chat endpoints
│   │   ├── ingest.py    # Document ingestion
│   │   └── admin.py     # Admin endpoints
│   └── dependencies.py   # FastAPI dependencies
├── agents/
│   ├── base.py          # Base agent class
│   ├── strategy_qa.py   # Strategy Q&A mode
│   ├── action_planner.py # Action recommendations
│   ├── analytics.py     # Analytics + Strategy mode
│   └── regulatory.py    # ERA regulatory mode
├── rag/
│   ├── retriever.py     # Hybrid retrieval logic
│   ├── vector_store.py  # Qdrant interface
│   ├── keyword_search.py # Postgres FTS
│   ├── rrf_fusion.py    # RRF implementation
│   └── embeddings.py    # Embedding generation
├── models/
│   ├── database.py      # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   └── enums.py         # Enumerations
├── services/
│   ├── chat_service.py  # Chat logic
│   ├── ingest_service.py # Document processing
│   ├── analytics_service.py # Analytics engine
│   └── auth_service.py  # Authentication
├── config/
│   ├── settings.py      # Configuration
│   └── database.py      # Database setup
└── utils/
    ├── logger.py        # Logging
    └── helpers.py       # Helper functions
```

## 🧠 Core Components

### Hybrid RAG System
1. **Semantic Search** (Qdrant) - conceptual understanding
2. **Keyword Search** (Postgres FTS) - exact term matching
3. **RRF Fusion** - intelligent result merging

### Agent Modes
- **Mode 1**: Strategy Q&A (RAG only)
- **Mode 2**: Action Planner (RAG + reasoning)
- **Mode 3**: Analytics + Strategy (RAG + analytics + alignment)
- **Mode 4**: Regulatory Advisor (ERA dataset + RAG)

### Analytics Engine
- Outage data aggregation
- KPI extraction
- Strategy alignment scoring
- Recommendation generation

## 🚀 Development

**Requirements**: Python 3.13+ (or 3.11+), PostgreSQL 14+

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy environment file and configure
cp .env.example .env
# Edit .env with your settings

# Run database migrations
alembic upgrade head

# Start the server
uvicorn main:app --reload --port 8000
```

## 🗄️ Database Migrations

This project uses Alembic for database migrations with async SQLAlchemy.

### Running Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Rollback all migrations
alembic downgrade base

# View current revision
alembic current

# View migration history
alembic history
```

### Creating New Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Create empty migration (for manual edits)
alembic revision -m "Description of changes"
```

### Notes

- The initial migration creates all tables, indexes, and FTS trigger
- FTS (Full-Text Search) uses a trigger to auto-update the `fts_vector` column
- All enum types are created as PostgreSQL ENUM types

## 🔧 Environment Variables

Create `.env`:

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost/sisuiq

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=  # Optional

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
EMBEDDING_MODEL=text-embedding-3-small

# Auth
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# App
ENVIRONMENT=development
LOG_LEVEL=INFO
```

## 📊 Database Schema

### Tables
- `users` - User accounts
- `sessions` - Chat sessions
- `chat_messages` - Message history
- `documents` - Ingested documents metadata
- `analytics_snapshots` - Cached analytics summaries
- `document_chunks` - Text chunks for FTS

## 🔌 API Endpoints

### Chat
- `POST /api/chat` - Send message, get agent response
- `GET /api/chat/sessions` - List user sessions
- `GET /api/chat/history/{session_id}` - Get session history

### Ingestion
- `POST /api/ingest/docs` - Upload strategy/ERA documents
- `POST /api/ingest/data` - Upload analytics data (CSV)
- `GET /api/ingest/status` - Check ingestion status

### Admin
- `GET /api/admin/sessions` - All sessions
- `GET /api/admin/documents` - Ingested documents
- `GET /api/admin/analytics` - Analytics snapshots
- `GET /api/admin/usage` - Model usage stats

## 🧪 Testing

```bash
pytest tests/
pytest tests/backend/ -v
pytest --cov=backend tests/backend/
```

## 📝 Development Notes

### Adding New Agent Mode
1. Create agent class in `agents/`
2. Extend `BaseAgent`
3. Implement `process()` method
4. Register in agent controller
5. Add tests

### Optimizing Retrieval
- Tune RRF weights in `rrf_fusion.py`
- Adjust embedding dimensions
- Configure FTS ranking in Postgres
- Cache frequent queries

### Performance
- Use async/await for I/O
- Implement connection pooling
- Cache embeddings
- Batch database operations
