"""
CaritasAI FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import routes_chat, routes_health
from app.api import routes_parishes, routes_events
# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Intelligent AI platform connecting Catholic volunteers with service opportunities",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes_health.router, tags=["Health"])
app.include_router(routes_chat.router, prefix="/api", tags=["Chat"])


app.include_router(routes_parishes.router, prefix="/api")
app.include_router(routes_events.router, prefix="/api")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to CaritasAI API",
        "description": "Connecting Catholic volunteers with service opportunities",
        "version": settings.VERSION,
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "chat": "/api/chat",
            "reset": "/api/chat/reset"
        }
    }


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    print("🙏 CaritasAI API starting...")
    print(f"✅ Environment: {settings.ENVIRONMENT}")
    print(f"✅ Agent initialized with model: {settings.CARITAS_MODEL}")
    print(f"📍 API running at http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"📚 API docs at http://{settings.API_HOST}:{settings.API_PORT}/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("👋 CaritasAI API shutting down...")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level="info"
    )