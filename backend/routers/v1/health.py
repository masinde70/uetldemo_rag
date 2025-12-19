"""API v1 - Health endpoints.

Provides health and status information about the API.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_db
from backend.services.health import check_all_services, get_degraded_capabilities

router = APIRouter()


class HealthResponse(BaseModel):
    """Basic health check response."""

    status: str
    version: str


class ServiceHealth(BaseModel):
    """Health status for a single service."""

    status: str
    latency_ms: float | None
    message: str | None


class DetailedHealthResponse(BaseModel):
    """Detailed health check response."""

    status: str
    version: str
    timestamp: str
    services: dict[str, ServiceHealth]
    capabilities: dict[str, bool]


@router.get("/health", response_model=HealthResponse)
async def health():
    """Basic health check.

    Returns 200 if the service is running.

    Returns:
        HealthResponse with status and version
    """
    return HealthResponse(
        status="ok",
        version="1.0.0",
    )


@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health(db: AsyncSession = Depends(get_db)):
    """Detailed health check with service status.

    Checks all dependencies (database, Qdrant, OpenAI) and returns
    their status along with capability flags.

    Returns:
        DetailedHealthResponse with service statuses and capabilities
    """
    health = await check_all_services(db)
    capabilities = get_degraded_capabilities(health)

    return DetailedHealthResponse(
        status=health.status.value,
        version="1.0.0",
        timestamp=health.timestamp.isoformat(),
        services={
            name: ServiceHealth(
                status=svc.status.value,
                latency_ms=svc.latency_ms,
                message=svc.message,
            )
            for name, svc in health.services.items()
        },
        capabilities=capabilities,
    )
