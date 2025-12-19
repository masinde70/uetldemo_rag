# API Documentation

SISUiQ provides both versioned (v1) and legacy (unversioned) API endpoints.

## API Versioning

**Recommended**: Use the versioned API (`/api/v1/`) for stability guarantees.

| Version | Prefix | Status |
|---------|--------|--------|
| v1 | `/api/v1/` | Stable |
| Legacy | `/api/` | Deprecated (will be removed in v2) |

## v1 API Endpoints

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Basic health check |
| GET | `/api/v1/health/detailed` | Detailed service status |

### Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chat` | Send message and get response |
| GET | `/api/v1/chat/modes` | List available chat modes |

### Sessions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/sessions` | List user's sessions |
| GET | `/api/v1/sessions/{id}` | Get session history |
| DELETE | `/api/v1/sessions/{id}` | Delete session |

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/documents` | List indexed documents |
| GET | `/api/v1/documents/{id}` | Get document details |
| GET | `/api/v1/documents/sources` | List document sources |

## Request/Response Examples

### POST /api/v1/chat

**Request:**
```json
{
  "message": "What is UETCL's strategic vision?",
  "mode": "strategy_qa",
  "session_id": null
}
```

**Response:**
```json
{
  "answer": "UETCL's strategic vision focuses on...",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "sources": ["uetcl-strategic-plan.pdf"],
  "agent": "strategy"
}
```

### GET /api/v1/health/detailed

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T12:00:00Z",
  "services": {
    "database": {"status": "healthy", "latency_ms": 5.2, "message": "Connected"},
    "qdrant": {"status": "healthy", "latency_ms": 12.8, "message": "Connected"},
    "openai": {"status": "healthy", "latency_ms": 250.5, "message": "Connected"}
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

## Authentication

Currently using header-based user identification:

```bash
curl -H "X-User-Email: user@example.com" \
  http://localhost:8000/api/v1/chat \
  -d '{"message": "Hello"}'
```

If no header provided, uses demo user.

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message here"
}
```

| Status Code | Description |
|-------------|-------------|
| 400 | Invalid request (bad mode, invalid ID format) |
| 404 | Resource not found |
| 403 | Forbidden (admin only) |
| 500 | Internal server error |

## Rate Limiting

Not currently implemented. Coming in v1.1.

## OpenAPI Documentation

Interactive docs available at:
- Swagger UI: `/api/docs`
- ReDoc: `/api/redoc`
- OpenAPI JSON: `/api/openapi.json`

## Migration from Legacy API

| Legacy Endpoint | v1 Endpoint |
|-----------------|-------------|
| `POST /api/chat` | `POST /api/v1/chat` |
| `GET /api/chat/sessions` | `GET /api/v1/sessions` |
| `GET /api/chat/history/{id}` | `GET /api/v1/sessions/{id}` |
| `GET /api/health` | `GET /api/v1/health` |
| `GET /api/health/detailed` | `GET /api/v1/health/detailed` |
