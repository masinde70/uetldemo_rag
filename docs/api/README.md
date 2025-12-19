# API Documentation

SISUiQ Backend API Reference

## Base URL

```
Development: http://localhost:8000
Production: https://api.sisuiq.com  # Example
```

## Authentication

Demo version uses JWT tokens (optional).

```bash
# Get token (if auth enabled)
curl -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Use token
curl -X GET http://localhost:8000/api/chat/sessions \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Chat API

### Send Message

**POST** `/api/chat`

Send a message to the AI agent and receive a response.

**Request Body**:
```json
{
  "message": "What are UETCL's key strategic objectives?",
  "session_id": "uuid-or-null",
  "mode": "strategy_qa",
  "include_analytics": false
}
```

**Parameters**:
- `message` (string, required): User query
- `session_id` (string, optional): Session ID for conversation continuity
- `mode` (string, required): Agent mode
  - `strategy_qa` - Strategy Q&A
  - `action_planner` - Action Recommendations
  - `analytics_strategy` - Analytics + Strategy
  - `regulatory_advisor` - ERA Regulatory Mode
- `include_analytics` (boolean, optional): Include analytics summary in context

**Response**:
```json
{
  "session_id": "uuid",
  "message_id": "uuid",
  "response": "UETCL's key strategic objectives include...",
  "citations": [
    {
      "document_id": "uuid",
      "title": "UETCL Strategic Plan 2024-2029",
      "page": 15,
      "excerpt": "...",
      "relevance_score": 0.92
    }
  ],
  "mode": "strategy_qa",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### List Sessions

**GET** `/api/chat/sessions`

Retrieve all chat sessions for the current user.

**Query Parameters**:
- `limit` (integer, optional): Max results (default: 50)
- `offset` (integer, optional): Pagination offset (default: 0)

**Response**:
```json
{
  "sessions": [
    {
      "id": "uuid",
      "mode": "strategy_qa",
      "created_at": "2024-01-15T10:00:00Z",
      "message_count": 12,
      "last_message": "What about grid modernization?"
    }
  ],
  "total": 45,
  "limit": 50,
  "offset": 0
}
```

### Get Session History

**GET** `/api/chat/history/{session_id}`

Retrieve all messages in a session.

**Response**:
```json
{
  "session_id": "uuid",
  "mode": "strategy_qa",
  "messages": [
    {
      "id": "uuid",
      "role": "user",
      "content": "What are the key objectives?",
      "timestamp": "2024-01-15T10:00:00Z"
    },
    {
      "id": "uuid",
      "role": "assistant",
      "content": "The key objectives are...",
      "citations": [...],
      "timestamp": "2024-01-15T10:00:05Z"
    }
  ]
}
```

---

## Ingestion API

### Ingest Documents

**POST** `/api/ingest/docs`

Upload and process strategy or regulatory documents.

**Request** (multipart/form-data):
- `file` (file, required): PDF file
- `doc_type` (string, required): `strategy` or `regulatory`
- `title` (string, optional): Document title
- `metadata` (json, optional): Additional metadata

**Response**:
```json
{
  "document_id": "uuid",
  "title": "UETCL Strategic Plan 2024-2029",
  "doc_type": "strategy",
  "chunks_created": 245,
  "embeddings_generated": 245,
  "status": "completed",
  "processing_time_seconds": 45.2
}
```

### Ingest Analytics Data

**POST** `/api/ingest/data`

Upload CSV analytics data (outages, metrics, etc.).

**Request** (multipart/form-data):
- `file` (file, required): CSV file
- `data_type` (string, required): `outages`, `metrics`, etc.
- `description` (string, optional): Data description

**Response**:
```json
{
  "snapshot_id": "uuid",
  "data_type": "outages",
  "rows_processed": 1250,
  "summary": {
    "total_outages": 1250,
    "total_duration_hours": 3425.5,
    "affected_customers": 125000,
    "top_causes": [
      {"cause": "Equipment Failure", "count": 450},
      {"cause": "Weather", "count": 320}
    ]
  },
  "status": "completed"
}
```

### Check Ingestion Status

**GET** `/api/ingest/status/{job_id}`

Check the status of an ingestion job.

**Response**:
```json
{
  "job_id": "uuid",
  "status": "processing",
  "progress": 65,
  "message": "Generating embeddings... 160/245 complete"
}
```

---

## Admin API

### Get All Sessions

**GET** `/api/admin/sessions`

Retrieve all sessions across all users.

**Query Parameters**:
- `mode` (string, optional): Filter by mode
- `start_date` (string, optional): Filter by date (YYYY-MM-DD)
- `end_date` (string, optional): Filter by date (YYYY-MM-DD)
- `limit` (integer, optional): Max results
- `offset` (integer, optional): Pagination offset

**Response**:
```json
{
  "sessions": [...],
  "total": 1250,
  "filters_applied": {
    "mode": "strategy_qa",
    "start_date": "2024-01-01"
  }
}
```

### List Documents

**GET** `/api/admin/documents`

Get all ingested documents.

**Query Parameters**:
- `doc_type` (string, optional): Filter by type
- `limit` (integer, optional): Max results
- `offset` (integer, optional): Pagination offset

**Response**:
```json
{
  "documents": [
    {
      "id": "uuid",
      "title": "UETCL Strategic Plan 2024-2029",
      "doc_type": "strategy",
      "source": "uploaded",
      "chunk_count": 245,
      "created_at": "2024-01-10T10:00:00Z",
      "metadata": {...}
    }
  ],
  "total": 87
}
```

### Get Analytics Snapshots

**GET** `/api/admin/analytics`

Retrieve analytics snapshots.

**Response**:
```json
{
  "snapshots": [
    {
      "id": "uuid",
      "data_source": "outages_2024_q1.csv",
      "created_at": "2024-01-15T10:00:00Z",
      "summary": {
        "total_outages": 1250,
        "total_duration_hours": 3425.5,
        "affected_customers": 125000
      }
    }
  ]
}
```

### Model Usage Statistics

**GET** `/api/admin/usage`

Get AI model usage statistics.

**Query Parameters**:
- `start_date` (string, optional): Start date (YYYY-MM-DD)
- `end_date` (string, optional): End date (YYYY-MM-DD)

**Response**:
```json
{
  "period": {
    "start": "2024-01-01",
    "end": "2024-01-31"
  },
  "total_requests": 3420,
  "total_tokens": 2450000,
  "costs": {
    "gpt4": 125.50,
    "embeddings": 2.35,
    "total": 127.85
  },
  "breakdown_by_mode": {
    "strategy_qa": 1250,
    "action_planner": 890,
    "analytics_strategy": 720,
    "regulatory_advisor": 560
  }
}
```

---

## Error Responses

All endpoints may return standard HTTP error codes:

### 400 Bad Request
```json
{
  "error": "validation_error",
  "message": "Invalid mode specified",
  "details": {
    "field": "mode",
    "allowed_values": ["strategy_qa", "action_planner", "analytics_strategy", "regulatory_advisor"]
  }
}
```

### 401 Unauthorized
```json
{
  "error": "unauthorized",
  "message": "Invalid or expired token"
}
```

### 404 Not Found
```json
{
  "error": "not_found",
  "message": "Session not found",
  "session_id": "uuid"
}
```

### 500 Internal Server Error
```json
{
  "error": "internal_error",
  "message": "An unexpected error occurred",
  "request_id": "uuid"
}
```

---

## Rate Limits

Demo version: No rate limits

Production:
- Chat API: 60 requests/minute per user
- Ingestion API: 10 requests/minute per user
- Admin API: 100 requests/minute

---

## Webhooks (Future)

Webhook support for:
- Document ingestion completion
- Analytics processing completion
- Usage threshold alerts

---

## OpenAPI/Swagger

Interactive API documentation available at:
```
http://localhost:8000/docs
```

Alternative ReDoc documentation:
```
http://localhost:8000/redoc
```
