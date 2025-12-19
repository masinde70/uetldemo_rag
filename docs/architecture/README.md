# SISUiQ Architecture

## System Overview

SISUiQ is a multi-layered AI copilot system designed to unify strategy, analytics, and regulatory intelligence for utility companies.

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  Next.js 15 • shadcn/ui • Tailwind CSS • TypeScript        │
└─────────────────────────┬───────────────────────────────────┘
                          │ REST API
┌─────────────────────────┴───────────────────────────────────┐
│                       Backend Layer                          │
│                    FastAPI • Python 3.13+                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Agent Router │  │ RAG Engine   │  │  Analytics   │     │
│  │              │  │              │  │   Engine     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────┬───────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
│   Qdrant     │  │  PostgreSQL  │  │   OpenAI    │
│   Vector DB  │  │  Relational  │  │   APIs      │
│              │  │      +       │  │             │
│   Semantic   │  │  Keyword     │  │  GPT-4.1    │
│   Search     │  │  Search (FTS)│  │  Embeddings │
└──────────────┘  └──────────────┘  └─────────────┘
```

## Data Flow

### 1. Document Ingestion Flow

```
PDF/Web Content
      │
      ▼
Parse & Chunk
      │
      ├─────────────────┬─────────────────┐
      ▼                 ▼                 ▼
Generate Embeddings   Extract Text    Store Metadata
      │                 │                 │
      ▼                 ▼                 ▼
   Qdrant          Postgres FTS      Postgres DB
```

### 2. Chat Query Flow

```
User Query
      │
      ▼
Agent Router
      │
      ├────────────┬────────────┬────────────┐
      ▼            ▼            ▼            ▼
  Strategy      Action      Analytics    Regulatory
  Q&A Mode      Planner     + Strategy   Advisor
      │            │            │            │
      └────────────┴────────────┴────────────┘
                   │
                   ▼
            Hybrid Retrieval
                   │
      ┌────────────┴────────────┐
      ▼                         ▼
Semantic Search          Keyword Search
 (Qdrant)                (Postgres FTS)
      │                         │
      └────────────┬────────────┘
                   ▼
              RRF Fusion
                   │
                   ▼
              Context Assembly
                   │
                   ▼
            LLM Generation (GPT-4.1)
                   │
                   ▼
            Response + Citations
```

### 3. Analytics Integration Flow

```
CSV Upload
      │
      ▼
Parse & Validate
      │
      ▼
Aggregate by Dimensions
  (cause, region, duration)
      │
      ▼
Generate Summary
      │
      ▼
Store Snapshot
      │
      ▼
Available for Agent Modes
```

## Hybrid RAG Architecture

### Why Hybrid?

Traditional vector-only RAG struggles with:
- Exact terms (policy numbers, KPIs, dates)
- Acronyms and codes
- Specific identifiers

Traditional keyword-only search struggles with:
- Conceptual queries
- Paraphrasing
- Synonyms

**Solution**: Combine both using RRF fusion

### Retrieval Pipeline

1. **Parallel Search**
   - Semantic: Query → Embedding → Qdrant → Top 20 results
   - Keyword: Query → FTS → Postgres → Top 20 results

2. **RRF Fusion**
   ```python
   score(doc) = Σ(1 / (k + rank_i))
   ```
   where:
   - `k` = 60 (constant)
   - `rank_i` = rank in search system i

3. **Deduplication & Reranking**
   - Merge results by document ID
   - Sort by combined RRF score
   - Return top N (typically 5-10)

### Benefits
- ✅ Catches exact terms AND concepts
- ✅ Robust to query variations
- ✅ Higher precision for hybrid content
- ✅ Better citation accuracy

## Agent Architecture

### Base Agent Interface

```python
class BaseAgent:
    def process(
        self,
        query: str,
        context: List[Document],
        analytics: Optional[AnalyticsSummary],
        history: List[Message]
    ) -> AgentResponse:
        pass
```

### Mode 1: Strategy Q&A

```
Query → Hybrid Retrieval → Context → LLM → Answer + Citations
```

**Purpose**: Direct answers from strategy documents
**Use Case**: "What are UETCL's key objectives for 2024-2029?"

### Mode 2: Action Planner

```
Query → Hybrid Retrieval → Context → LLM (reasoning) → Action Items
```

**Purpose**: Turn strategy into actionable steps
**Use Case**: "Create an action plan for grid modernization"

### Mode 3: Analytics + Strategy

```
Query → [Hybrid Retrieval + Analytics Summary] → Context → LLM →
  Data-Driven Recommendations + Strategy Alignment
```

**Purpose**: Combine operational data with strategic goals
**Use Case**: "Based on outage data, what should we prioritize?"

### Mode 4: Regulatory Advisor

```
Query → Hybrid Retrieval (ERA docs) → Context → LLM →
  Compliance Guidance + Requirements
```

**Purpose**: ERA compliance and regulatory mapping
**Use Case**: "What are ERA's requirements for transmission reliability?"

## Database Schema

### PostgreSQL Tables

```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Sessions
CREATE TABLE sessions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    mode VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Chat Messages
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions(id),
    role VARCHAR(20),
    content TEXT,
    citations JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Documents
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    title VARCHAR(500),
    source VARCHAR(255),
    doc_type VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Document Chunks (for FTS)
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(id),
    chunk_index INTEGER,
    content TEXT,
    content_vector tsvector,
    metadata JSONB,
    CONSTRAINT unique_doc_chunk UNIQUE (document_id, chunk_index)
);

CREATE INDEX idx_content_fts ON document_chunks
    USING GIN (content_vector);

-- Analytics Snapshots
CREATE TABLE analytics_snapshots (
    id UUID PRIMARY KEY,
    summary JSONB,
    data_source VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Qdrant Collection Schema

```python
collection_config = {
    "vectors": {
        "size": 1536,  # text-embedding-3-small
        "distance": "Cosine"
    },
    "payload_schema": {
        "document_id": "keyword",
        "chunk_index": "integer",
        "content": "text",
        "title": "text",
        "source": "keyword",
        "doc_type": "keyword",
        "metadata": "json"
    }
}
```

## Testing Architecture

### End-to-End (E2E) Testing
- **Framework**: Playwright
- **Configuration**: Root-level `playwright.config.ts`
- **Test Location**: `/tests` directory
- **Features**:
  - Automated browser testing (Chromium)
  - Integrated web server management (starts frontend automatically)
  - Failure reporting with screenshots and traces

### Verification Workflow
1. **Frontend**: Next.js development server is started with Turbopack.
2. **Backend**: FastAPI services are expected to be running or containerized.
3. **Execution**: Tests simulate user interactions across the dashboard, chat, and analytics modules.

## Scalability Considerations

### Current (Demo) Scale
- Documents: ~100 PDFs
- Chunks: ~10,000 chunks
- Users: Single user demo
- Queries: <100/day

### Production Scale Targets
- Documents: 10,000+ PDFs
- Chunks: 1M+ chunks
- Users: 100-1000 concurrent
- Queries: 10,000+/day

### Scaling Strategies

1. **Qdrant**
   - Use quantization for smaller index size
   - Implement sharding for >1M vectors
   - Add Qdrant cluster for HA

2. **PostgreSQL**
   - Connection pooling (pgbouncer)
   - Read replicas for analytics
   - Partitioning for large tables

3. **Caching**
   - Redis for frequent queries
   - Embedding cache for common phrases
   - Analytics snapshot cache

4. **API Layer**
   - Horizontal scaling with load balancer
   - Rate limiting per user
   - Request queuing for expensive operations

## Security Architecture

### Authentication
- JWT tokens (demo)
- OAuth2 for production
- Role-based access control

### Data Security
- Encrypted connections (TLS)
- Encrypted at rest (database)
- API key rotation
- Audit logging

### Input Validation
- Pydantic schemas
- SQL injection prevention (ORM)
- XSS prevention (sanitization)
- File upload validation

## Monitoring & Observability

### Metrics to Track
- Query latency (p50, p95, p99)
- Retrieval accuracy (citation relevance)
- LLM token usage
- Error rates
- Cache hit rates

### Logging
- Structured logs (JSON)
- Request/response logging
- Error tracking (Sentry)
- Agent decision logging

### Dashboards
- Real-time usage metrics
- Model performance
- Cost tracking
- User analytics
