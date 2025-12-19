"""Request tracing with trace_id propagation for SISUiQ.

Provides:
- Trace ID generation and propagation
- X-Trace-Id header handling
- Context variable for request-scoped trace_id

Each incoming request gets a trace_id:
- Accept X-Trace-Id if present in request headers
- Otherwise generate a new UUID
- Attach trace_id to response header X-Trace-Id
- Make trace_id available in logs via context variable
"""
import uuid
from contextvars import ContextVar
from typing import Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

# Context variable for request-scoped trace_id
_trace_id: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)


def get_trace_id() -> Optional[str]:
    """
    Get the current trace_id from request context.
    
    Returns:
        The trace_id string or None if not in a request context
    """
    return _trace_id.get()


def set_trace_id(trace_id: str) -> None:
    """
    Set the trace_id for the current request context.
    
    Args:
        trace_id: The trace ID string
    """
    _trace_id.set(trace_id)


def generate_trace_id() -> str:
    """
    Generate a new trace_id.
    
    Returns:
        A new UUID string for tracing
    """
    return str(uuid.uuid4())


class TraceMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for request tracing.
    
    Features:
    - Accepts X-Trace-Id header from client if present
    - Generates new trace_id if not provided
    - Sets trace_id in context variable for logging
    - Adds X-Trace-Id to response headers
    
    Usage:
        app.add_middleware(TraceMiddleware)
    """
    
    TRACE_HEADER = "X-Trace-Id"
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Get trace_id from header or generate new one
        trace_id = request.headers.get(self.TRACE_HEADER)
        
        if not trace_id:
            trace_id = generate_trace_id()
        
        # Set in context for logging
        set_trace_id(trace_id)
        
        # Process request
        response = await call_next(request)
        
        # Add trace_id to response headers
        response.headers[self.TRACE_HEADER] = trace_id
        
        return response
