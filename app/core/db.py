from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

# Async engine and session factory
# settings.DATABASE_URL should be set in `.env`. Examples:
# - Postgres: postgresql+asyncpg://user:pass@localhost:5432/puddle_db
# - SQLite (dev): sqlite+aiosqlite:///./puddle_dev.db
engine = create_async_engine(settings.ASYNC_DATABASE_URL, future=True, echo=False)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def get_session():
    """Yield an async SQLAlchemy session."""
    async with AsyncSessionLocal() as session:
        yield session
