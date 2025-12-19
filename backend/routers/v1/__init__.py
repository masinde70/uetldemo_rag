"""API v1 - Versioned API endpoints.

This module provides the v1 API with stable, documented endpoints.
All endpoints are prefixed with /api/v1/.

Version: 1.0.0
Stability: Stable
"""

from fastapi import APIRouter

from backend.routers.v1.chat import router as chat_router
from backend.routers.v1.documents import router as documents_router
from backend.routers.v1.health import router as health_router
from backend.routers.v1.sessions import router as sessions_router

# Create main v1 router
router = APIRouter(prefix="/api/v1")

# Include sub-routers
router.include_router(health_router, tags=["v1-health"])
router.include_router(chat_router, tags=["v1-chat"])
router.include_router(sessions_router, tags=["v1-sessions"])
router.include_router(documents_router, tags=["v1-documents"])

__all__ = ["router"]
