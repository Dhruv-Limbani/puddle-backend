from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or .env file."""

    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/puddle_db"
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    ASYNC_DATABASE_URL: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    def model_post_init(self, __context):
        """Automatically compute async DB URL after initialization."""
        self.ASYNC_DATABASE_URL = normalize_async_db_url(self.DATABASE_URL)


def normalize_async_db_url(dsn: str) -> str:
    """Ensure the DSN uses the asyncpg driver for SQLAlchemy async engine."""
    if not dsn:
        return dsn
    if "+asyncpg" in dsn:
        return dsn
    if dsn.startswith("postgresql://"):
        return dsn.replace("postgresql://", "postgresql+asyncpg://", 1)
    return dsn


# Instantiate settings singleton
settings = Settings()
