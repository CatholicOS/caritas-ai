"""
Database Configuration

Handles both PostgreSQL (production) and SQLite (testing)
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator
import os

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# If no DATABASE_URL, try to import from config
if not DATABASE_URL:
    try:
        from app.core.config import settings
        DATABASE_URL = settings.DATABASE_URL
    except:
        # Default to SQLite for testing
        DATABASE_URL = "sqlite:///:memory:"

# Create engine with appropriate settings based on database type
if DATABASE_URL and DATABASE_URL.startswith("sqlite"):
    # SQLite configuration (for testing)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    # PostgreSQL configuration (for production)
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=False
    )

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    Yields a database session and closes it when done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database - create all tables.
    Used in testing and initial setup.
    """
    Base.metadata.create_all(bind=engine)


def drop_db():
    """
    Drop all database tables.
    Used in testing cleanup.
    """
    Base.metadata.drop_all(bind=engine)