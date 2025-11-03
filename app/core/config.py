from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Use DATABASE_URL from .env — default shown as Postgres pattern; replace in .env
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/puddle_db"
    ASYNC_DATABASE_URL: str | None = None
    OPENAI_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None

    model_config = {
        "env_file": ".env",  # Pydantic v2 syntax for Config
    }


settings = Settings()


def normalize_async_db_url(dsn: str) -> str:
    """Ensure the DSN uses the asyncpg driver for SQLAlchemy async engine.

    - If already contains '+asyncpg' returns as-is.
    - If it's a postgres DSN without asyncpg, inject '+asyncpg'.
    """
    if not dsn:
        return dsn
    if "+asyncpg" in dsn:
        return dsn
    # Only transform postgres scheme; leave other DSNs untouched
    if dsn.startswith("postgresql://"):
        return dsn.replace("postgresql://", "postgresql+asyncpg://", 1)
    return dsn


# Expose a computed async DB URL so callers (db.py) don't need to guess
settings.ASYNC_DATABASE_URL = normalize_async_db_url(settings.DATABASE_URL)
