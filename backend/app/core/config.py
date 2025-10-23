from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    app_env: str = os.getenv("APP_ENV", "dev")
    app_port: int = int(os.getenv("APP_PORT", "8000"))
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY", None)
    database_url: str | None = os.getenv("DATABASE_URL", None)
    cors_origins: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:8501").split(",")

settings = Settings()
