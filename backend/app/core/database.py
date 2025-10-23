from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from .config import settings

engine = None
SessionLocal = None

if settings.database_url:
    engine = create_async_engine(settings.database_url, future=True, echo=False)
    SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_db() -> AsyncSession:
    if SessionLocal is None:
        raise RuntimeError("Database URL not configured")
    async with SessionLocal() as session:
        yield session
