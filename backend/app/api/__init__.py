
"""
API Router Configuration

This file registers all API routes with the FastAPI app.
"""

from fastapi import APIRouter
from app.api import routes_health, routes_chat, routes_parishes, routes_events

api_router = APIRouter()

# Include all route modules
api_router.include_router(routes_health.router, tags=["health"])
api_router.include_router(routes_chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(routes_parishes.router, prefix="/api", tags=["parishes"])
api_router.include_router(routes_events.router, prefix="/api", tags=["events"])