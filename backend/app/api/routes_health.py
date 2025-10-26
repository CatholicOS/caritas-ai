"""
Health Check API Routes
"""

from fastapi import APIRouter
from pydantic import BaseModel
from app.core.config import settings

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    service: str
    version: str
    environment: str
    ai_agent: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify API is running.
    
    Returns:
    - Service status
    - Version information
    - Environment
    - AI agent details
    
    This endpoint is useful for:
    - Monitoring
    - Load balancer health checks
    - Deployment verification
    """
    return HealthResponse(
        status="healthy",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        ai_agent=f"CaritasAI with {settings.CARITAS_MODEL}"
    )


@router.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check with more information.
    
    Returns additional details about:
    - Configuration
    - Database connection (when implemented)
    - External services (when implemented)
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "ai_config": {
            "model": settings.CARITAS_MODEL,
            "temperature": 0.7,
            "provider": "OpenAI"
        },
        "database": {
            "connected": False,  #: Check actual database connection
            "url": "Not configured" if not settings.DATABASE_URL else "Configured"
        },
        "features": {
            "agentic_ai": True,
            "tool_calling": True,
            "memory": True,
            "geospatial": False  #: Enable when PostGIS is set up
        }
    }