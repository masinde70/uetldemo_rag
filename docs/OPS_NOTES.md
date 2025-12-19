# Operations Notes

This document covers operational aspects of running SISUiQ in production and development environments.

## Health & Readiness

SISUiQ provides multiple health check endpoints for different purposes:

### Liveness Probe (`/api/health`)
Fast, always-available endpoint that confirms the API is running.
- **Purpose**: Container orchestration liveness checks
- **Response time**: <10ms
- **Does not**: Check external dependencies

```bash
curl http://localhost/api/health
# {"status":"ok"}
```

### Readiness/Detailed Health (`/api/health/detailed`)
Comprehensive health check that verifies all dependencies.
- **Purpose**: Load balancer readiness, monitoring dashboards
- **Response time**: 1-2 seconds (includes OpenAI ping)
- **Checks**: PostgreSQL, Qdrant, OpenAI

```bash
curl http://localhost/api/health/detailed
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-19T07:46:18.587904",
  "services": {
    "database": {"status": "healthy", "latency_ms": 42.0},
    "qdrant": {"status": "healthy", "latency_ms": 20.0},
    "openai": {"status": "healthy", "latency_ms": 1238.0}
  },
  "capabilities": {
    "chat": true,
    "streaming": true,
    "session_history": true,
    "document_retrieval": true,
    "analytics": true,
    "admin": true,
    "file_upload": true
  }
}
```

### Docker Healthchecks
The `docker-compose.yml` configures healthchecks for:
- **postgres**: `pg_isready` command
- **qdrant**: HTTP health endpoint
- **backend**: `/api/health` endpoint
- **nginx**: Process check

## Retries & Timeouts

### Startup Retries
The backend retries connections on startup for resilience to cold starts:

| Service | Max Retries | Initial Delay | Max Delay |
|---------|-------------|---------------|-----------|
| Qdrant | 10 | 2s | 30s |
| PostgreSQL | 5 | 1s | 30s |

Configure via environment variables:
```bash
MAX_RETRIES=5
INITIAL_RETRY_DELAY=1.0
MAX_RETRY_DELAY=30.0
BACKOFF_MULTIPLIER=2.0
```

### Request Timeouts
External service calls have explicit timeouts:

| Service | Default Timeout | Environment Variable |
|---------|-----------------|---------------------|
| OpenAI | 60s | `OPENAI_TIMEOUT` |
| Qdrant | 30s | `QDRANT_TIMEOUT` |
| Database | 10s | `DB_TIMEOUT` |
| Web Fetch | 30s | `WEB_FETCH_TIMEOUT` |

### Error Responses
On timeout, the API returns a structured error with trace_id:
```json
{
  "detail": "OpenAI API call timed out after 60s (trace_id: abc123)",
  "trace_id": "abc123"
}
```

## Background Ingestion Jobs

Large PDF ingestion runs in the background to avoid HTTP timeouts.

### Async Ingestion Flow
1. `POST /api/ingest/docs/async` - Queue document, returns immediately
2. `GET /api/ingest/jobs/{job_id}` - Poll for status
3. Background worker processes: extract → chunk → embed → store

### Job States
- `queued` - Waiting for worker
- `running` - Currently processing
- `done` - Successfully completed
- `failed` - Error occurred (check `error_message`)

### Example Usage
```bash
# Queue a document
curl -X POST http://localhost/api/ingest/docs/async \
  -F "file=@document.pdf" \
  -F "doc_type=strategy" \
  -F "source=uetcl"

# Response
{"job_id": "abc-123", "status": "queued", "message": "Document queued..."}

# Poll status
curl http://localhost/api/ingest/jobs/abc-123

# Response when running
{"job_id": "abc-123", "status": "running", "progress": 60, ...}

# Response when done
{"job_id": "abc-123", "status": "done", "progress": 100, "chunks_count": 42, ...}
```

## Document Lifecycle

### Delete Document
Removes document, all chunks, and Qdrant vectors:
```bash
curl -X DELETE http://localhost/api/admin/documents/{id} \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### Reindex Document
Re-extracts, re-chunks, and re-embeds from stored file:
```bash
curl -X POST http://localhost/api/admin/documents/{id}/reindex \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

Use reindexing when:
- Chunking parameters have changed
- Embedding model was updated
- Search quality seems degraded for specific documents

## Monitoring

### Key Metrics to Watch
1. **API Response Times**: P95 should be <2s for chat, <100ms for health
2. **Background Job Queue**: Should not grow unbounded
3. **OpenAI Latency**: Typically 1-3s, alert if consistently >10s
4. **Qdrant Search Latency**: Should be <100ms
5. **Database Connections**: Pool usage should stay <80%

### Log Analysis
Important log patterns:
```bash
# Successful ingestion
grep "Completed ingestion job" /var/log/sisuiq/*.log

# Failed jobs
grep "Ingestion job .* failed" /var/log/sisuiq/*.log

# Timeout errors
grep "timed out" /var/log/sisuiq/*.log

# Retry attempts
grep "Retry \d+/\d+" /var/log/sisuiq/*.log
```

## Troubleshooting

### Backend won't start
1. Check Postgres is healthy: `docker compose ps postgres`
2. Check Qdrant is healthy: `docker compose ps qdrant`
3. View backend logs: `docker compose logs backend --tail 50`

### Ingestion jobs stuck in "queued"
1. Verify worker is running (check startup logs)
2. Check for exceptions in logs
3. Restart backend to reset worker

### Search returns no results
1. Verify documents exist: `GET /api/admin/documents`
2. Check Qdrant collection: `curl http://localhost:6333/collections`
3. Try reindexing: `POST /api/admin/documents/{id}/reindex`

### High latency
1. Check `/api/health/detailed` for slow services
2. Review OpenAI rate limits
3. Check database connection pool saturation
