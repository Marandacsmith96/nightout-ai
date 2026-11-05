"""Central configuration for the NightOut AI backend.

All secrets come from environment variables (`.env` at the backend root).
Nothing sensitive is ever hardcoded here.
"""
from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv

# Load backend/.env if present (missing file is fine — env vars may already be set).
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"))


@lru_cache
def _raw_origins() -> list[str]:
    raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    return [o.strip() for o in raw.split(",") if o.strip()]


@lru_cache
def _has_places_key() -> bool:
    return bool((os.getenv("GOOGLE_PLACES_API_KEY") or "").strip())


class Settings:
    """Thin, plain wrapper around environment variables."""

    @property
    def allowed_origins(self) -> list[str]:
        return _raw_origins()

    @property
    def demo_mode(self) -> bool:
        """No Google Places key => venue retrieval falls back to demo data."""
        return not _has_places_key()

    @property
    def openai_api_key(self) -> str:
        return os.getenv("OPENAI_API_KEY", "").strip()

    @property
    def openai_base_url(self) -> str | None:
        return os.getenv("OPENAI_BASE_URL", "").strip() or None

    @property
    def openai_model(self) -> str:
        return os.getenv("OPENAI_MODEL", "").strip() or None

    @property
    def google_places_api_key(self) -> str:
        return os.getenv("GOOGLE_PLACES_API_KEY", "").strip()

    @property
    def google_routes_api_key(self) -> str:
        return os.getenv("GOOGLE_ROUTES_API_KEY", "").strip()

    @property
    def ticketmaster_api_key(self) -> str:
        return os.getenv("TICKETMASTER_API_KEY", "").strip()


settings = Settings()
