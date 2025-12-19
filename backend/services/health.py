"""Health check services for monitoring system dependencies.

This module provides health checks for all external services:
- PostgreSQL database
- Qdrant vector database
- OpenAI API

Used for both /health endpoints and graceful degradation logic.
"""

import asyncio
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from openai import AsyncOpenAI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.qdrant import get_client


class ServiceStatus(str, Enum):
    """Service health status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class ServiceHealth:
    """Health status for a single service."""

    name: str
    status: ServiceStatus
    latency_ms: Optional[float] = None
    message: Optional[str] = None
    last_checked: Optional[datetime] = None


@dataclass
class SystemHealth:
    """Overall system health including all services."""

    status: ServiceStatus
    services: dict[str, ServiceHealth]
    timestamp: datetime

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "services": {
                name: {
                    "status": svc.status.value,
                    "latency_ms": svc.latency_ms,
                    "message": svc.message,
                }
                for name, svc in self.services.items()
            },
        }


async def check_database(db: AsyncSession) -> ServiceHealth:
    """Check PostgreSQL database health."""
    start = asyncio.get_event_loop().time()

    try:
        await db.execute(text("SELECT 1"))
        latency = (asyncio.get_event_loop().time() - start) * 1000

        return ServiceHealth(
            name="database",
            status=ServiceStatus.HEALTHY if latency < 100 else ServiceStatus.DEGRADED,
            latency_ms=round(latency, 2),
            message="Connected" if latency < 100 else "Slow response",
            last_checked=datetime.utcnow(),
        )
    except Exception as e:
        return ServiceHealth(
            name="database",
            status=ServiceStatus.UNHEALTHY,
            message=str(e)[:100],
            last_checked=datetime.utcnow(),
        )


async def check_qdrant() -> ServiceHealth:
    """Check Qdrant vector database health."""
    start = asyncio.get_event_loop().time()

    try:
        client = await get_client()
        # Simple health check - get collections
        await asyncio.wait_for(
            asyncio.to_thread(client.get_collections),
            timeout=5.0,
        )
        latency = (asyncio.get_event_loop().time() - start) * 1000

        return ServiceHealth(
            name="qdrant",
            status=ServiceStatus.HEALTHY if latency < 200 else ServiceStatus.DEGRADED,
            latency_ms=round(latency, 2),
            message="Connected" if latency < 200 else "Slow response",
            last_checked=datetime.utcnow(),
        )
    except asyncio.TimeoutError:
        return ServiceHealth(
            name="qdrant",
            status=ServiceStatus.UNHEALTHY,
            message="Connection timeout",
            last_checked=datetime.utcnow(),
        )
    except Exception as e:
        return ServiceHealth(
            name="qdrant",
            status=ServiceStatus.UNHEALTHY,
            message=str(e)[:100],
            last_checked=datetime.utcnow(),
        )


async def check_openai() -> ServiceHealth:
    """Check OpenAI API health."""
    start = asyncio.get_event_loop().time()

    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return ServiceHealth(
                name="openai",
                status=ServiceStatus.UNHEALTHY,
                message="API key not configured",
                last_checked=datetime.utcnow(),
            )

        client = AsyncOpenAI(api_key=api_key)

        # Minimal API call to verify connectivity
        await asyncio.wait_for(
            client.models.list(),
            timeout=10.0,
        )
        latency = (asyncio.get_event_loop().time() - start) * 1000

        return ServiceHealth(
            name="openai",
            status=ServiceStatus.HEALTHY if latency < 2000 else ServiceStatus.DEGRADED,
            latency_ms=round(latency, 2),
            message="Connected" if latency < 2000 else "High latency",
            last_checked=datetime.utcnow(),
        )
    except asyncio.TimeoutError:
        return ServiceHealth(
            name="openai",
            status=ServiceStatus.UNHEALTHY,
            message="Connection timeout",
            last_checked=datetime.utcnow(),
        )
    except Exception as e:
        error_msg = str(e)[:100]
        # Check for rate limiting
        if "rate" in error_msg.lower():
            return ServiceHealth(
                name="openai",
                status=ServiceStatus.DEGRADED,
                message="Rate limited",
                last_checked=datetime.utcnow(),
            )
        return ServiceHealth(
            name="openai",
            status=ServiceStatus.UNHEALTHY,
            message=error_msg,
            last_checked=datetime.utcnow(),
        )


async def check_all_services(db: AsyncSession) -> SystemHealth:
    """Check health of all services concurrently."""
    # Run all health checks in parallel
    db_health, qdrant_health, openai_health = await asyncio.gather(
        check_database(db),
        check_qdrant(),
        check_openai(),
    )

    services = {
        "database": db_health,
        "qdrant": qdrant_health,
        "openai": openai_health,
    }

    # Determine overall status
    statuses = [svc.status for svc in services.values()]

    if all(s == ServiceStatus.HEALTHY for s in statuses):
        overall = ServiceStatus.HEALTHY
    elif any(s == ServiceStatus.UNHEALTHY for s in statuses):
        overall = ServiceStatus.UNHEALTHY
    else:
        overall = ServiceStatus.DEGRADED

    return SystemHealth(
        status=overall,
        services=services,
        timestamp=datetime.utcnow(),
    )


def get_degraded_capabilities(health: SystemHealth) -> dict:
    """Determine which features are available based on service health.

    Returns a dict of feature flags indicating what's available.
    """
    db_healthy = health.services["database"].status != ServiceStatus.UNHEALTHY
    qdrant_healthy = health.services["qdrant"].status != ServiceStatus.UNHEALTHY
    openai_healthy = health.services["openai"].status != ServiceStatus.UNHEALTHY

    return {
        # Core chat requires all services
        "chat": db_healthy and qdrant_healthy and openai_healthy,
        # Streaming requires same as chat
        "streaming": db_healthy and qdrant_healthy and openai_healthy,
        # Session history only needs database
        "session_history": db_healthy,
        # Document retrieval needs Qdrant
        "document_retrieval": qdrant_healthy,
        # Analytics needs database
        "analytics": db_healthy,
        # Admin operations need database
        "admin": db_healthy,
        # File upload needs database and Qdrant
        "file_upload": db_healthy and qdrant_healthy,
    }
