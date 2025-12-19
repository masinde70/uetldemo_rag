"""Structured logging with Loguru for SISUiQ.

Provides:
- Colorful, readable console logs
- JSON-formatted logs (optional)
- Request/response logging middleware
- Contextual logging (trace_id, user_id, session_id, mode)
- Exception logging with stack traces

Example console log output:
2024-12-17 10:30:00.123 | INFO     | request_end | POST /api/chat | 200 | 1234ms | trace_id=abc-123
"""
import sys
import time
from contextvars import ContextVar
from typing import Any, Optional

from loguru import logger
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

# Context variables for request-scoped data
_user_id: ContextVar[Optional[str]] = ContextVar("user_id", default=None)
_session_id: ContextVar[Optional[str]] = ContextVar("session_id", default=None)
_mode: ContextVar[Optional[str]] = ContextVar("mode", default=None)


def set_user_id(user_id: str) -> None:
    """Set user_id for current request context."""
    _user_id.set(user_id)


def set_session_id(session_id: str) -> None:
    """Set session_id for current request context."""
    _session_id.set(session_id)


def set_mode(mode: str) -> None:
    """Set chat mode for current request context."""
    _mode.set(mode)


def get_user_id() -> Optional[str]:
    """Get user_id from current request context."""
    return _user_id.get()


def get_session_id() -> Optional[str]:
    """Get session_id from current request context."""
    return _session_id.get()


def get_mode() -> Optional[str]:
    """Get chat mode from current request context."""
    return _mode.get()


def _get_context_string() -> str:
    """Build context string for logging."""
    from backend.observability.tracing import get_trace_id
    
    parts = []
    
    trace_id = get_trace_id()
    if trace_id:
        parts.append(f"trace_id={trace_id}")
    
    user_id = get_user_id()
    if user_id:
        parts.append(f"user_id={user_id}")
    
    session_id = get_session_id()
    if session_id:
        parts.append(f"session_id={session_id}")
    
    mode = get_mode()
    if mode:
        parts.append(f"mode={mode}")
    
    return " | ".join(parts) if parts else ""


def configure_logging(json_logs: bool = False) -> None:
    """
    Configure loguru for logging.
    
    Args:
        json_logs: If True, output JSON logs. If False, colorful console logs.
    
    Call this once at application startup.
    """
    # Remove default handler
    logger.remove()
    
    if json_logs:
        # JSON format for production
        logger.add(
            sys.stdout,
            format="{message}",
            level="INFO",
            serialize=True,
        )
    else:
        # Colorful console format for development
        logger.add(
            sys.stdout,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            ),
            level="INFO",
            colorize=True,
        )
    
    logger.info("🚀 Loguru logging configured")


def get_logger(name: str = "sisuiq"):
    """
    Get a loguru logger with context binding.
    
    Args:
        name: Logger name (defaults to "sisuiq")
    
    Returns:
        Configured loguru logger
    """
    return logger.bind(name=name)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for request/response logging.
    
    Logs:
    - Request start: method, path
    - Request end: method, path, status, duration_ms
    - Exceptions: full stack trace
    - Chat lifecycle: rag_ms, llm_ms, analytics_ms (via context)
    """
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Skip logging for health checks and metrics
        if request.url.path in ("/api/health", "/metrics"):
            return await call_next(request)
        
        start_time = time.perf_counter()
        
        # Build query string
        query = f"?{request.query_params}" if request.query_params else ""
        
        # Log request start
        logger.info(f"→ {request.method} {request.url.path}{query}")
        
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            # Get context
            ctx = _get_context_string()
            ctx_part = f" | {ctx}" if ctx else ""
            
            # Log request end with status color
            status = response.status_code
            if status < 400:
                logger.info(
                    f"← {request.method} {request.url.path} | {status} | {duration_ms:.0f}ms{ctx_part}"
                )
            elif status < 500:
                logger.warning(
                    f"← {request.method} {request.url.path} | {status} | {duration_ms:.0f}ms{ctx_part}"
                )
            else:
                logger.error(
                    f"← {request.method} {request.url.path} | {status} | {duration_ms:.0f}ms{ctx_part}"
                )
            
            return response
            
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            ctx = _get_context_string()
            ctx_part = f" | {ctx}" if ctx else ""
            
            # Log exception with stack trace
            logger.exception(
                f"✖ {request.method} {request.url.path} | {duration_ms:.0f}ms | {exc}{ctx_part}"
            )
            raise


def log_chat_lifecycle(
    rag_ms: Optional[float] = None,
    llm_ms: Optional[float] = None,
    analytics_ms: Optional[float] = None,
) -> None:
    """
    Log chat request lifecycle timings.
    
    Call this at the end of /api/chat to log component durations.
    """
    parts = ["📊 Chat lifecycle:"]
    
    if rag_ms is not None:
        parts.append(f"RAG={rag_ms:.0f}ms")
    if llm_ms is not None:
        parts.append(f"LLM={llm_ms:.0f}ms")
    if analytics_ms is not None:
        parts.append(f"Analytics={analytics_ms:.0f}ms")
    
    ctx = _get_context_string()
    if ctx:
        parts.append(f"| {ctx}")
    
    logger.info(" ".join(parts))


# Convenience exports
info = logger.info
debug = logger.debug
warning = logger.warning
error = logger.error
exception = logger.exception
success = logger.success
