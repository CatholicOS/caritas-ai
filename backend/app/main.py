from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api import routes_chat, routes_health

app = FastAPI(title="CaritasAI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_health.router, prefix="/health", tags=["health"])
app.include_router(routes_chat.router, prefix="/chat", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "CaritasAI API is running", "env": settings.app_env}
