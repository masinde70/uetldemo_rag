"""Prometheus metrics for SISUiQ.

Provides:
- Counters: chat_requests_total, rag_queries_total, analytics_runs_total
- Histograms: rag_duration_seconds, llm_duration_seconds, request_duration_seconds
- GET /metrics endpoint in Prometheus text format
- Middleware for automatic request duration tracking

Example usage:
    from backend.observability.metrics import CHAT_REQUESTS, RAG_DURATION
    
    # Increment counter
    CHAT_REQUESTS.labels(mode="strategy_qa", status="success").inc()
    
    # Record histogram
    with RAG_DURATION.labels(mode="strategy_qa").time():
        # do RAG query
        pass
"""
import time
from typing import Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

# Use prometheus_client for metrics
try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        Counter,
        Histogram,
        generate_latest,
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    # Provide no-op implementations if prometheus_client is not installed
    class NoOpMetric:
        def labels(self, **kwargs):
            return self
        def inc(self, amount=1):
            pass
        def observe(self, value):
            pass
        def time(self):
            return NoOpContext()
    
    class NoOpContext:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
    
    Counter = lambda *args, **kwargs: NoOpMetric()
    Histogram = lambda *args, **kwargs: NoOpMetric()


# --- Counters ---

CHAT_REQUESTS = Counter(
    "chat_requests_total",
    "Total number of chat requests",
    ["mode", "status"],
) if PROMETHEUS_AVAILABLE else NoOpMetric()

RAG_QUERIES = Counter(
    "rag_queries_total", 
    "Total number of RAG queries",
    ["mode"],
) if PROMETHEUS_AVAILABLE else NoOpMetric()

ANALYTICS_RUNS = Counter(
    "analytics_runs_total",
    "Total number of analytics pipeline runs",
    ["dataset"],
) if PROMETHEUS_AVAILABLE else NoOpMetric()


# --- Histograms ---

# Define buckets for different duration ranges
DURATION_BUCKETS = (0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0)
LLM_BUCKETS = (0.5, 1.0, 2.0, 3.0, 5.0, 7.5, 10.0, 15.0, 20.0, 30.0, 60.0)

RAG_DURATION = Histogram(
    "rag_duration_seconds",
    "RAG query duration in seconds",
    ["mode"],
    buckets=DURATION_BUCKETS,
) if PROMETHEUS_AVAILABLE else NoOpMetric()

LLM_DURATION = Histogram(
    "llm_duration_seconds",
    "LLM inference duration in seconds",
    ["mode", "model"],
    buckets=LLM_BUCKETS,
) if PROMETHEUS_AVAILABLE else NoOpMetric()

REQUEST_DURATION = Histogram(
    "request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path", "status"],
    buckets=DURATION_BUCKETS,
) if PROMETHEUS_AVAILABLE else NoOpMetric()


# --- Metrics Endpoint ---

def setup_metrics(app: FastAPI) -> None:
    """
    Add /metrics endpoint to FastAPI app.
    
    Returns metrics in Prometheus text exposition format.
    """
    if not PROMETHEUS_AVAILABLE:
        @app.get("/metrics")
        async def metrics_not_available():
            return Response(
                content="# prometheus_client not installed\n",
                media_type="text/plain",
                status_code=200,
            )
        return
    
    @app.get("/metrics")
    async def metrics():
        """Prometheus metrics endpoint."""
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST,
        )


# --- Metrics Middleware ---

class MetricsMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for automatic request duration tracking.
    
    Records request_duration_seconds histogram for all requests
    except /metrics and /api/health endpoints.
    """
    
    SKIP_PATHS = {"/metrics", "/api/health"}
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Skip metrics for health checks and metrics endpoint
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)
        
        start_time = time.perf_counter()
        
        response = await call_next(request)
        
        # Record duration
        duration = time.perf_counter() - start_time
        
        # Normalize path to avoid high cardinality
        # Replace UUIDs and IDs with placeholders
        path = self._normalize_path(request.url.path)
        
        REQUEST_DURATION.labels(
            method=request.method,
            path=path,
            status=str(response.status_code),
        ).observe(duration)
        
        return response
    
    def _normalize_path(self, path: str) -> str:
        """
        Normalize path to reduce cardinality.
        
        Replaces:
        - UUIDs with {id}
        - Numeric IDs with {id}
        """
        import re
        
        # Replace UUIDs
        path = re.sub(
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            "{id}",
            path,
            flags=re.IGNORECASE,
        )
        
        # Replace numeric IDs (e.g., /users/123)
        path = re.sub(r"/\d+(?=/|$)", "/{id}", path)
        
        return path


# --- Helper Functions ---

def observe_rag_duration(mode: str, duration_seconds: float) -> None:
    """
    Record RAG query duration.
    
    Args:
        mode: Chat mode (strategy_qa, regulatory, etc.)
        duration_seconds: Query duration in seconds
    """
    RAG_DURATION.labels(mode=mode).observe(duration_seconds)
    RAG_QUERIES.labels(mode=mode).inc()


def observe_llm_duration(
    mode: str, duration_seconds: float, model: str = "gpt-4"
) -> None:
    """
    Record LLM inference duration.
    
    Args:
        mode: Chat mode
        duration_seconds: Inference duration in seconds
        model: Model name (default: gpt-4)
    """
    LLM_DURATION.labels(mode=mode, model=model).observe(duration_seconds)


def record_chat_request(mode: str, success: bool = True) -> None:
    """
    Increment chat request counter.
    
    Args:
        mode: Chat mode
        success: Whether request was successful
    """
    status = "success" if success else "error"
    CHAT_REQUESTS.labels(mode=mode, status=status).inc()


def record_analytics_run(dataset: str) -> None:
    """
    Increment analytics run counter.
    
    Args:
        dataset: Dataset name that was processed
    """
    ANALYTICS_RUNS.labels(dataset=dataset).inc()
