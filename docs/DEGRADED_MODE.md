# Degraded Mode & Service Health

SISUiQ includes comprehensive health monitoring and graceful degradation to maintain user experience when services are unavailable or performing slowly.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend                                │
│  ┌─────────────────┐     ┌────────────────────────────┐    │
│  │ useServiceHealth│────▶│     StatusBanner           │    │
│  │     Hook        │     │  (Shows warnings)          │    │
│  └────────┬────────┘     └────────────────────────────┘    │
│           │                                                  │
│           ▼ polls every 30s                                 │
└───────────┼─────────────────────────────────────────────────┘
            │
            ▼
┌───────────────────────────────────────────────────────────────┐
│                    Backend                                     │
│  ┌───────────────────────────────────────────────────────┐   │
│  │          /api/health/detailed                          │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │   │
│  │  │ Database │  │  Qdrant  │  │  OpenAI  │            │   │
│  │  │  Check   │  │  Check   │  │  Check   │            │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘            │   │
│  │       └──────────────┴──────────────┘                 │   │
│  │                      │                                 │   │
│  │              ┌───────▼───────┐                        │   │
│  │              │  Capabilities  │                        │   │
│  │              │    Matrix     │                        │   │
│  │              └───────────────┘                        │   │
│  └───────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────┘
```

## Health Endpoints

### GET /api/health
Basic liveness check. Returns 200 if process is running.

```json
{"status": "ok"}
```

### GET /api/health/detailed
Comprehensive health with service status and capabilities.

```json
{
  "status": "degraded",
  "timestamp": "2024-01-15T12:00:00Z",
  "services": {
    "database": {
      "status": "healthy",
      "latency_ms": 5.2,
      "message": "Connected"
    },
    "qdrant": {
      "status": "healthy",
      "latency_ms": 12.8,
      "message": "Connected"
    },
    "openai": {
      "status": "degraded",
      "latency_ms": 2500,
      "message": "High latency"
    }
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

### GET /api/health/ready
Kubernetes readiness probe. Returns 503 if system can't handle traffic.

### GET /api/health/live
Kubernetes liveness probe. Always returns 200 if process is alive.

## Service Status Levels

| Status | Description | Latency Threshold |
|--------|-------------|-------------------|
| `healthy` | Service responding normally | < threshold |
| `degraded` | Service slow but functional | > threshold |
| `unhealthy` | Service unavailable | timeout/error |

### Latency Thresholds

| Service | Healthy | Degraded |
|---------|---------|----------|
| Database | < 100ms | 100-5000ms |
| Qdrant | < 200ms | 200-5000ms |
| OpenAI | < 2000ms | 2000-10000ms |

## Capability Matrix

Features are enabled/disabled based on service health:

| Capability | Database | Qdrant | OpenAI |
|------------|----------|--------|--------|
| Chat | Required | Required | Required |
| Streaming | Required | Required | Required |
| Session History | Required | - | - |
| Document Retrieval | - | Required | - |
| Analytics | Required | - | - |
| Admin | Required | - | - |
| File Upload | Required | Required | - |

## Frontend Integration

### useServiceHealth Hook

```typescript
import { useServiceHealth } from "@/lib/hooks";

function MyComponent() {
  const {
    health,        // Full health status
    isOnline,      // Browser network status
    isHealthy,     // All services healthy
    isDegraded,    // Some services slow
    isLoading,     // Fetching health
    refresh,       // Manual refresh
  } = useServiceHealth({
    pollInterval: 30000,  // 30 seconds
    onStatusChange: (status) => {
      // Called when status changes
      if (status.status === "unhealthy") {
        showNotification("Service issues detected");
      }
    },
  });

  // Check capability before action
  if (!health?.capabilities.chat) {
    return <ChatUnavailable />;
  }

  return <Chat />;
}
```

### StatusBanner Component

```tsx
import { StatusBanner, StatusIndicator } from "@/components/StatusBanner";

function Layout() {
  const { health, isOnline, isLoading, refresh } = useServiceHealth();

  return (
    <div>
      <StatusBanner
        health={health}
        isOnline={isOnline}
        isLoading={isLoading}
        onRefresh={refresh}
      />

      {/* In topbar */}
      <StatusIndicator health={health} isOnline={isOnline} />
    </div>
  );
}
```

## Graceful Degradation Strategies

### 1. Chat Unavailable

When chat is unavailable (OpenAI/Qdrant down):

```tsx
if (!health?.capabilities.chat) {
  return (
    <div className="offline-message">
      <h2>Chat temporarily unavailable</h2>
      <p>We're experiencing technical difficulties. Please try again later.</p>
      <button onClick={refresh}>Check again</button>
    </div>
  );
}
```

### 2. Slow Responses

When services are degraded:

```tsx
if (health?.status === "degraded") {
  return (
    <Chat
      showSlowWarning={true}
      timeout={60000}  // Increased timeout
    />
  );
}
```

### 3. Session History Only

When only database is available:

```tsx
if (!health?.capabilities.chat && health?.capabilities.session_history) {
  return (
    <div>
      <p>New messages unavailable, but you can view your history:</p>
      <SessionHistory />
    </div>
  );
}
```

### 4. Complete Offline

When browser is offline:

```tsx
if (!isOnline) {
  return (
    <OfflinePage>
      <p>You're currently offline.</p>
      <p>Connect to the internet to use SISUiQ.</p>
    </OfflinePage>
  );
}
```

## Monitoring & Alerts

### Prometheus Metrics

Health checks expose metrics for monitoring:

```
# Service health status (1=healthy, 0.5=degraded, 0=unhealthy)
sisuiq_service_health{service="database"} 1
sisuiq_service_health{service="qdrant"} 1
sisuiq_service_health{service="openai"} 0.5

# Service latency
sisuiq_service_latency_ms{service="database"} 5.2
sisuiq_service_latency_ms{service="qdrant"} 12.8
sisuiq_service_latency_ms{service="openai"} 2500
```

### Alert Examples

```yaml
# Alert on service unhealthy for > 5 minutes
- alert: ServiceUnhealthy
  expr: sisuiq_service_health == 0
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "Service {{ $labels.service }} is unhealthy"

# Alert on high latency
- alert: HighLatency
  expr: sisuiq_service_latency_ms > 5000
  for: 2m
  labels:
    severity: warning
```

## Testing Degraded Mode

### Simulate Service Failures

```bash
# Stop Qdrant
docker-compose stop qdrant

# Verify degraded response
curl http://localhost:8000/api/health/detailed | jq

# Restart
docker-compose start qdrant
```

### Frontend Testing

```typescript
// Mock health hook in tests
jest.mock("@/lib/hooks", () => ({
  useServiceHealth: () => ({
    health: {
      status: "degraded",
      capabilities: { chat: false, session_history: true },
    },
    isOnline: true,
    isHealthy: false,
    isDegraded: true,
  }),
}));
```

## Best Practices

1. **Always check capabilities** before performing actions
2. **Show clear feedback** to users about what's unavailable
3. **Provide retry options** for transient failures
4. **Cache last-known-good data** when possible
5. **Log health transitions** for debugging
6. **Set appropriate timeouts** based on degraded status
