"""Health check endpoints for monitoring and degraded mode support.

Provides detailed health status for all system dependencies,
enabling frontend graceful degradation.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_db
from backend.services.health import (
    ServiceStatus,
    check_all_services,
    get_degraded_capabilities,
)

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def basic_health():
    """Basic health check - always returns 200 if service is running."""
    return {"status": "ok"}


@router.get("/health/detailed")
async def detailed_health(db: AsyncSession = Depends(get_db)):
    """Detailed health check with all service statuses.

    Returns:
        - status: overall system status (healthy/degraded/unhealthy)
        - services: individual service health with latency
        - capabilities: feature flags based on available services

    Used by frontend to determine which features to enable/disable.
    """
    health = await check_all_services(db)
    capabilities = get_degraded_capabilities(health)

    response = health.to_dict()
    response["capabilities"] = capabilities

    return response


@router.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Kubernetes-style readiness probe.

    Returns 200 if system can handle traffic, 503 otherwise.
    """
    health = await check_all_services(db)

    if health.status == ServiceStatus.UNHEALTHY:
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "message": "One or more critical services unavailable",
                "services": {
                    name: svc.status.value
                    for name, svc in health.services.items()
                },
            },
        )

    return {"status": "ready"}


@router.get("/health/live")
async def liveness_check():
    """Kubernetes-style liveness probe.

    Always returns 200 if the process is running.
    Used to detect hung processes.
    """
    return {"status": "alive"}
