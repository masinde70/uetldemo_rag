"""Observability package for SISUiQ backend.

Provides:
- Structured JSON logging with structlog
- Request tracing with trace_id propagation
- Prometheus metrics (counters, histograms)
- Optional OpenTelemetry integration

Usage:
    from backend.observability import setup_observability
    
    # In main.py lifespan
    setup_observability(app)
"""

from backend.observability.logging import (
    configure_logging,
    get_logger,
    LoggingMiddleware,
)
from backend.observability.tracing import (
    TraceMiddleware,
    get_trace_id,
    set_trace_id,
)
from backend.observability.metrics import (
    MetricsMiddleware,
    setup_metrics,
    CHAT_REQUESTS,
    RAG_QUERIES,
    ANALYTICS_RUNS,
    RAG_DURATION,
    LLM_DURATION,
    REQUEST_DURATION,
)

__all__ = [
    # Logging
    "configure_logging",
    "get_logger",
    "LoggingMiddleware",
    # Tracing
    "TraceMiddleware", 
    "get_trace_id",
    "set_trace_id",
    # Metrics
    "MetricsMiddleware",
    "setup_metrics",
    "CHAT_REQUESTS",
    "RAG_QUERIES",
    "ANALYTICS_RUNS",
    "RAG_DURATION",
    "LLM_DURATION",
    "REQUEST_DURATION",
    # Setup
    "setup_observability",
]


def setup_observability(app):
    """
    Configure all observability features for the FastAPI app.
    
    Adds:
    - Structured JSON logging
    - Request tracing middleware
    - Prometheus metrics middleware and endpoint
    - Optional OpenTelemetry instrumentation
    """
    from fastapi import FastAPI
    
    if not isinstance(app, FastAPI):
        raise TypeError("Expected FastAPI app instance")
    
    # 1. Configure structured logging
    configure_logging()
    logger = get_logger()
    logger.info("observability_init", message="Initializing observability")
    
    # 2. Add tracing middleware (must be added first for trace_id)
    app.add_middleware(TraceMiddleware)
    
    # 3. Add logging middleware
    app.add_middleware(LoggingMiddleware)
    
    # 4. Add metrics middleware and endpoint
    setup_metrics(app)
    app.add_middleware(MetricsMiddleware)
    
    # 5. Optional: OpenTelemetry instrumentation
    _setup_otel(app)
    
    logger.info("observability_ready", message="Observability configured")


def _setup_otel(app):
    """
    Setup OpenTelemetry instrumentation if OTEL_EXPORTER_OTLP_ENDPOINT is set.
    """
    import os
    
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not endpoint:
        return
    
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        
        resource = Resource.create({
            "service.name": os.getenv("OTEL_SERVICE_NAME", "sisuiq-backend"),
            "service.version": "0.1.0",
        })
        
        provider = TracerProvider(resource=resource)
        processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint))
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        
        FastAPIInstrumentor.instrument_app(app)
        
        logger = get_logger()
        logger.info("otel_enabled", endpoint=endpoint)
        
    except ImportError:
        logger = get_logger()
        logger.warning(
            "otel_not_available",
            message="OpenTelemetry packages not installed. "
                    "Install with: pip install opentelemetry-api opentelemetry-sdk "
                    "opentelemetry-exporter-otlp opentelemetry-instrumentation-fastapi"
        )
