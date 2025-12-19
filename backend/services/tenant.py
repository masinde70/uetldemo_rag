"""Multi-tenant support service.

Provides tenant isolation and management for enterprise deployments.
This is a foundation for multi-tenant support - full implementation
would require database schema changes.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class TenantTier(str, Enum):
    """Tenant subscription tiers."""

    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


@dataclass
class TenantConfig:
    """Configuration for a tenant."""

    id: UUID
    name: str
    slug: str  # URL-friendly identifier
    tier: TenantTier
    max_users: int
    max_documents: int
    max_queries_per_day: int
    custom_branding: bool
    api_access: bool
    created_at: datetime
    settings: dict

    @classmethod
    def default_for_tier(cls, tier: TenantTier, name: str, slug: str) -> "TenantConfig":
        """Create tenant with default settings for tier."""
        tier_defaults = {
            TenantTier.FREE: {
                "max_users": 3,
                "max_documents": 10,
                "max_queries_per_day": 50,
                "custom_branding": False,
                "api_access": False,
            },
            TenantTier.STARTER: {
                "max_users": 10,
                "max_documents": 100,
                "max_queries_per_day": 500,
                "custom_branding": False,
                "api_access": True,
            },
            TenantTier.PROFESSIONAL: {
                "max_users": 50,
                "max_documents": 1000,
                "max_queries_per_day": 5000,
                "custom_branding": True,
                "api_access": True,
            },
            TenantTier.ENTERPRISE: {
                "max_users": -1,  # Unlimited
                "max_documents": -1,
                "max_queries_per_day": -1,
                "custom_branding": True,
                "api_access": True,
            },
        }

        defaults = tier_defaults[tier]
        return cls(
            id=uuid4(),
            name=name,
            slug=slug,
            tier=tier,
            created_at=datetime.utcnow(),
            settings={},
            **defaults,
        )


class TenantContext:
    """Context manager for tenant-scoped operations."""

    _current_tenant: Optional[TenantConfig] = None

    @classmethod
    def set_tenant(cls, tenant: TenantConfig) -> None:
        """Set the current tenant context."""
        cls._current_tenant = tenant

    @classmethod
    def get_tenant(cls) -> Optional[TenantConfig]:
        """Get the current tenant context."""
        return cls._current_tenant

    @classmethod
    def clear(cls) -> None:
        """Clear the tenant context."""
        cls._current_tenant = None

    @classmethod
    def require_tenant(cls) -> TenantConfig:
        """Get tenant or raise if not set."""
        if cls._current_tenant is None:
            raise ValueError("No tenant context set")
        return cls._current_tenant


def get_tenant_from_request(
    host: str,
    api_key: Optional[str] = None,
) -> Optional[TenantConfig]:
    """Resolve tenant from request information.

    Multi-tenancy resolution order:
    1. API key header (for programmatic access)
    2. Subdomain (e.g., tenant1.sisuiq.com)
    3. Default tenant for single-tenant deployments

    Args:
        host: Request host header
        api_key: Optional API key

    Returns:
        TenantConfig if resolved, None otherwise
    """
    # TODO: Implement actual tenant resolution from database

    # For now, return a default single tenant
    return TenantConfig.default_for_tier(
        tier=TenantTier.ENTERPRISE,
        name="Default",
        slug="default",
    )


def check_tenant_limits(
    tenant: TenantConfig,
    users_count: int = 0,
    documents_count: int = 0,
    daily_queries: int = 0,
) -> dict[str, bool]:
    """Check if tenant is within their limits.

    Args:
        tenant: The tenant config
        users_count: Current user count
        documents_count: Current document count
        daily_queries: Queries made today

    Returns:
        Dict with limit check results
    """
    def check_limit(current: int, max_val: int) -> bool:
        return max_val == -1 or current < max_val

    return {
        "users_ok": check_limit(users_count, tenant.max_users),
        "documents_ok": check_limit(documents_count, tenant.max_documents),
        "queries_ok": check_limit(daily_queries, tenant.max_queries_per_day),
    }


# Middleware helper for FastAPI
async def tenant_middleware(request, call_next):
    """FastAPI middleware for tenant resolution.

    Usage:
        app.middleware("http")(tenant_middleware)
    """
    # Resolve tenant from request
    host = request.headers.get("host", "")
    api_key = request.headers.get("x-api-key")

    tenant = get_tenant_from_request(host, api_key)

    if tenant:
        TenantContext.set_tenant(tenant)

    try:
        response = await call_next(request)
        return response
    finally:
        TenantContext.clear()
