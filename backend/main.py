"""SISUiQ API - FastAPI Backend for ERA/UETCL Strategy Copilot."""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

from backend.db import close_db
from backend.routers import admin, auth, chat, chat_stream, health, ingest
from backend.routers.v1 import router as v1_router
from backend.services.qdrant import close_client, ensure_collection
from backend.services.ingestion_jobs import start_worker, stop_worker


# --- HTTPS Enforcement Middleware ---

class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce HTTPS in production.
    
    Redirects HTTP requests to HTTPS when:
    - ENFORCE_HTTPS env var is "true"
    - Request is not already HTTPS
    - Request is not to health check endpoints
    """
    
    async def dispatch(self, request: Request, call_next):
        # Check if HTTPS enforcement is enabled
        enforce_https = os.getenv("ENFORCE_HTTPS", "false").lower() == "true"
        
        if enforce_https:
            # Check if request is HTTPS (via X-Forwarded-Proto header from load balancer)
            forwarded_proto = request.headers.get("x-forwarded-proto", "http")
            
            # Skip health checks to allow load balancer health probes
            if request.url.path in ["/api/health", "/api/health/ready", "/api/health/live"]:
                return await call_next(request)
            
            # Redirect HTTP to HTTPS
            if forwarded_proto != "https" and request.url.scheme != "https":
                url = request.url.replace(scheme="https")
                return RedirectResponse(url=str(url), status_code=301)
        
        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown."""
    # Startup
    await ensure_collection()
    
    # Start background ingestion worker
    start_worker()
    
    yield
    
    # Shutdown
    await stop_worker()
    await close_db()
    await close_client()


app = FastAPI(
    title="SISUiQ API",
    description="ERA/UETCL Strategy & Regulatory Copilot API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Setup observability first (logging, tracing, metrics)
# This must be done before other middleware to ensure proper ordering
try:
    from backend.observability import setup_observability
    setup_observability(app)
except ImportError:
    # Observability packages not installed, skip
    pass

# HTTPS enforcement middleware (must be before CORS)
app.add_middleware(HTTPSRedirectMiddleware)

# CORS middleware - added after observability so traces/metrics capture CORS headers
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - legacy (unversioned)
app.include_router(auth.router)  # Auth router first
app.include_router(admin.router)
app.include_router(chat.router)
app.include_router(chat_stream.router)
app.include_router(health.router)
app.include_router(ingest.router)

# Include versioned API
app.include_router(v1_router)


@app.get("/api/version")
async def version():
    """Version information endpoint."""
    return {
        "version": "0.1.0",
        "name": "SISUiQ API",
        "environment": os.getenv("ENVIRONMENT", "development"),
    }
