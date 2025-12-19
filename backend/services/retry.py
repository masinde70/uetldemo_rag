"""Retry logic and timeout utilities for resilient operations.

Provides capped exponential backoff for startup dependencies and
explicit timeouts for external service calls.
"""
import asyncio
import functools
import os
from typing import Any, Callable, Optional, TypeVar
from loguru import logger

# Timeout configuration (seconds)
OPENAI_TIMEOUT = float(os.getenv("OPENAI_TIMEOUT", "60"))
QDRANT_TIMEOUT = float(os.getenv("QDRANT_TIMEOUT", "30"))
DB_TIMEOUT = float(os.getenv("DB_TIMEOUT", "10"))
WEB_FETCH_TIMEOUT = float(os.getenv("WEB_FETCH_TIMEOUT", "30"))

# Retry configuration
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "5"))
INITIAL_DELAY = float(os.getenv("INITIAL_RETRY_DELAY", "1.0"))
MAX_DELAY = float(os.getenv("MAX_RETRY_DELAY", "30.0"))
BACKOFF_MULTIPLIER = float(os.getenv("BACKOFF_MULTIPLIER", "2.0"))

T = TypeVar("T")


class RetryError(Exception):
    """Raised when all retry attempts are exhausted."""

    def __init__(self, message: str, attempts: int, last_error: Optional[Exception] = None):
        self.attempts = attempts
        self.last_error = last_error
        super().__init__(message)


class TimeoutError(Exception):
    """Raised when an operation times out."""

    def __init__(self, message: str, timeout: float, trace_id: Optional[str] = None):
        self.timeout = timeout
        self.trace_id = trace_id
        super().__init__(message)


def calculate_backoff(attempt: int) -> float:
    """Calculate backoff delay with exponential growth and cap.
    
    Args:
        attempt: Current attempt number (1-indexed)
        
    Returns:
        Delay in seconds
    """
    delay = INITIAL_DELAY * (BACKOFF_MULTIPLIER ** (attempt - 1))
    return min(delay, MAX_DELAY)


async def retry_async(
    func: Callable[..., Any],
    *args,
    max_retries: int = MAX_RETRIES,
    retryable_exceptions: tuple = (Exception,),
    on_retry: Optional[Callable[[int, Exception], None]] = None,
    **kwargs,
) -> Any:
    """Execute async function with retry logic.
    
    Args:
        func: Async function to execute
        *args: Positional arguments for func
        max_retries: Maximum retry attempts
        retryable_exceptions: Tuple of exception types to retry on
        on_retry: Optional callback on retry (attempt, exception)
        **kwargs: Keyword arguments for func
        
    Returns:
        Result of successful function call
        
    Raises:
        RetryError: If all attempts fail
    """
    last_error: Optional[Exception] = None
    
    for attempt in range(1, max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except retryable_exceptions as e:
            last_error = e
            
            if attempt < max_retries:
                delay = calculate_backoff(attempt)
                logger.warning(
                    f"Retry {attempt}/{max_retries} for {func.__name__} "
                    f"after {type(e).__name__}: {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                
                if on_retry:
                    on_retry(attempt, e)
                    
                await asyncio.sleep(delay)
            else:
                logger.error(
                    f"All {max_retries} attempts failed for {func.__name__}: {e}"
                )
    
    raise RetryError(
        f"Failed after {max_retries} attempts",
        attempts=max_retries,
        last_error=last_error,
    )


async def with_timeout(
    coro,
    timeout: float,
    operation_name: str = "operation",
    trace_id: Optional[str] = None,
) -> Any:
    """Execute coroutine with timeout.
    
    Args:
        coro: Coroutine to execute
        timeout: Timeout in seconds
        operation_name: Name for error messages
        trace_id: Optional trace ID for error tracking
        
    Returns:
        Result of coroutine
        
    Raises:
        TimeoutError: If operation times out
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        error_msg = f"{operation_name} timed out after {timeout}s"
        if trace_id:
            error_msg += f" (trace_id: {trace_id})"
        logger.error(error_msg)
        raise TimeoutError(error_msg, timeout=timeout, trace_id=trace_id)


def timeout_decorator(timeout: float, operation_name: Optional[str] = None):
    """Decorator to add timeout to async functions.
    
    Args:
        timeout: Timeout in seconds
        operation_name: Optional name for error messages
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            name = operation_name or func.__name__
            trace_id = kwargs.get("trace_id")
            return await with_timeout(
                func(*args, **kwargs),
                timeout=timeout,
                operation_name=name,
                trace_id=trace_id,
            )
        return wrapper
    return decorator


async def wait_for_postgres(
    engine,
    max_retries: int = MAX_RETRIES,
) -> bool:
    """Wait for PostgreSQL to be available.
    
    Args:
        engine: SQLAlchemy async engine
        max_retries: Maximum retry attempts
        
    Returns:
        True if connection successful
        
    Raises:
        RetryError: If connection fails after all retries
    """
    from sqlalchemy import text
    
    async def check_connection():
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            return True
    
    logger.info("Waiting for PostgreSQL connection...")
    
    result = await retry_async(
        check_connection,
        max_retries=max_retries,
        retryable_exceptions=(Exception,),
        on_retry=lambda attempt, e: logger.debug(f"Postgres connection attempt {attempt} failed"),
    )
    
    logger.info("✅ PostgreSQL connection established")
    return result


async def wait_for_qdrant(
    client,
    max_retries: int = MAX_RETRIES,
) -> bool:
    """Wait for Qdrant to be available.
    
    Args:
        client: Qdrant async client
        max_retries: Maximum retry attempts
        
    Returns:
        True if connection successful
        
    Raises:
        RetryError: If connection fails after all retries
    """
    async def check_connection():
        await client.get_collections()
        return True
    
    logger.info("Waiting for Qdrant connection...")
    
    result = await retry_async(
        check_connection,
        max_retries=max_retries,
        retryable_exceptions=(Exception,),
        on_retry=lambda attempt, e: logger.debug(f"Qdrant connection attempt {attempt} failed"),
    )
    
    logger.info("✅ Qdrant connection established")
    return result


# Convenience functions for service calls with timeouts
async def call_openai_with_timeout(coro, trace_id: Optional[str] = None):
    """Execute OpenAI call with configured timeout."""
    return await with_timeout(
        coro,
        timeout=OPENAI_TIMEOUT,
        operation_name="OpenAI API call",
        trace_id=trace_id,
    )


async def call_qdrant_with_timeout(coro, trace_id: Optional[str] = None):
    """Execute Qdrant call with configured timeout."""
    return await with_timeout(
        coro,
        timeout=QDRANT_TIMEOUT,
        operation_name="Qdrant call",
        trace_id=trace_id,
    )


async def call_db_with_timeout(coro, trace_id: Optional[str] = None):
    """Execute database call with configured timeout."""
    return await with_timeout(
        coro,
        timeout=DB_TIMEOUT,
        operation_name="Database call",
        trace_id=trace_id,
    )
