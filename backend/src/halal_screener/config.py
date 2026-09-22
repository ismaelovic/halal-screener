"""Application configuration, read from environment / .env."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    APP_ENV: str = "development"

    # Falls back to local SQLite for zero-setup local dev; point this at a
    # Supabase Postgres connection string in production
    # (postgresql+psycopg2://...).
    DATABASE_URL: str = "sqlite:///./halal_screener.db"

    EODHD_API_KEY: str = ""

    # How long a cached FinancialRatios row (by `fetched_at`) is trusted
    # before a live re-fetch is triggered for that ticker.
    FUNDAMENTALS_TTL_HOURS: int = 24


@lru_cache
def get_settings() -> Settings:
    return Settings()
