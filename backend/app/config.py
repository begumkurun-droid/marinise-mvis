"""
MARINISE MVIS - central configuration.

All values are read from environment variables (see .env.example at repo root).
No credentials or paid-API keys are hard-coded, per Section 18 of the master
prompt ("API anahtarları frontend kodunda görünmemelidir" / "Secret management").
"""
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Core ---
    environment: str = "development"
    secret_key: str = "change-me-in-.env"  # noqa: S105 - placeholder only
    access_token_expire_minutes: int = 60 * 8

    # --- Database ---
    database_url: str = (
        "postgresql+psycopg://marinise:marinise@localhost:5432/marinise"
    )

    # --- Cache / queue ---
    redis_url: str = "redis://localhost:6379/0"

    # --- AIS ingestion ---
    # AISStream offers a free tier (see FAZ 0 feasibility report). The key is
    # the user's own free API key - never purchased or hard-coded here.
    aisstream_api_key: str | None = None
    aisstream_ws_url: str = "wss://stream.aisstream.io/v0/stream"

    # --- AI provider adapter (Section 17: must stay swappable) ---
    ai_provider: str = "none"  # "claude" | "openai" | "none"
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None

    # --- CORS ---
    # Plain string, not list[str]: pydantic-settings tries to JSON-decode a
    # list-typed env var before any validator runs, which breaks on a plain
    # comma-separated value (e.g. Render's env var UI). Kept as a string and
    # split in the cors_origins property below instead.
    cors_origins_raw: str = Field(default="http://localhost:3000", validation_alias="CORS_ORIGINS")

    @field_validator("database_url", mode="before")
    @classmethod
    def _normalize_database_url(cls, v: str) -> str:
        # Managed Postgres hosts (e.g. Render) hand out "postgres://" or
        # plain "postgresql://" connection strings; psycopg3 needs the
        # explicit "postgresql+psycopg://" driver scheme.
        if v.startswith("postgres://"):
            return "postgresql+psycopg://" + v[len("postgres://") :]
        if v.startswith("postgresql://"):
            return "postgresql+psycopg://" + v[len("postgresql://") :]
        return v

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
