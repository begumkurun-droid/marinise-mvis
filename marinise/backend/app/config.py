"""
MARINISE MVIS - central configuration.

All values are read from environment variables (see .env.example at repo root).
No credentials or paid-API keys are hard-coded, per Section 18 of the master
prompt ("API anahtarları frontend kodunda görünmemelidir" / "Secret management").
"""
from functools import lru_cache
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
    cors_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
