"""
Health check endpoints for service monitoring.

Provides endpoints for infrastructure health checks used by:
- Kubernetes liveness/readiness probes
- Load balancer health checks
- Monitoring systems

Example:
    GET /health
    >>> {"status": "healthy", "version": "1.0.0"}
"""

from fastapi import APIRouter

from application.dtos.responses import HealthResponse
from infrastructure.config.settings import get_setting

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Check service health status.

    Returns basic health information including service status and version.
    This endpoint should always return quickly and not depend on external
    services to avoid cascading failures in health checks.

    Returns:
        HealthResponse with status and version information.

    Example:
        >>> response = await client.get("/health")
        >>> assert response.json()["status"] == "healthy"
    """
    settings = get_setting()
    return HealthResponse(status="healthy", version=settings.app_version)
