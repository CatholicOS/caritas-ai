"""
Application Configuration
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # Project Information
    PROJECT_NAME: str = "CaritasAI API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    
    # CORS Origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000"
    ]
    
    # OpenAI Configuration
    
    OPENAI_API_KEY: str = ""
    CARITAS_MODEL: str = "gpt-4o"  # or gpt-3
    CARITAS_TEMPERATURE: float = 0.7
    
    # Database Configuration
    DATABASE_URL: str = ""
    DATABASE_URL_ASYNC: str = ""
    
    # External Services
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    
    GOOGLE_MAPS_API_KEY: str = ""
    
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = ""
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Feature Flags
    USE_MOCK_DATA: bool = True
    ENABLE_SMS: bool = False
    ENABLE_EMAIL: bool = False
    ENABLE_WHATSAPP: bool = False
    
    # Logging
    LOG_LEVEL: str = "info"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()


# Validate critical settings
def validate_settings():
    """Validate that critical settings are configured."""
    if not settings.OPENAI_API_KEY:
        print("⚠️  WARNING: OPENAI_API_KEY not set. Agent will not work!")
        print("   Set it in your .env file or environment variables.")
    
    if settings.ENVIRONMENT == "production":
        if settings.SECRET_KEY == "your-secret-key-change-in-production":
            raise ValueError("SECRET_KEY must be changed in production!")
        
        if not settings.DATABASE_URL:
            print("⚠️  WARNING: DATABASE_URL not set in production!")


# Run validation on import
validate_settings()