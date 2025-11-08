from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Optional: control SQL echo via environment
ECHO_SQL = False

# Async SQLAlchemy engine and session
engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    future=True,
    echo=ECHO_SQL
)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


async def get_session():
    """Dependency for FastAPI routes: yields an async session."""
    async with AsyncSessionLocal() as session:
        yield session


async def close_engine():
    """Gracefully dispose the database engine (useful in shutdown events or tests)."""
    await engine.dispose()
