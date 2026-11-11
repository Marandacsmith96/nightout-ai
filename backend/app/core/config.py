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

    # --- Phase 7: multimodal media (promo poster + voice-over) ---

    @property
    def flux_base_url(self) -> str | None:
        """FLUX image endpoint (OpenAI-compatible /images/generations)."""
        return os.getenv("FLUX_BASE_URL", "").strip() or None

    @property
    def flux_api_key(self) -> str:
        return os.getenv("FLUX_API_KEY", "").strip()

    @property
    def flux_model(self) -> str:
        return os.getenv("FLUX_MODEL", "black-forest-labs/FLUX.2-klein-4B").strip()

    @property
    def flux_configured(self) -> bool:
        return bool(self.flux_base_url and self.flux_api_key)

    @property
    def tts_base_url(self) -> str | None:
        """Chatterbox TTS endpoint (OpenAI-compatible /v1/audio/speech)."""
        return os.getenv("TTS_BASE_URL", "").strip() or None

    @property
    def tts_api_key(self) -> str:
        return os.getenv("TTS_API_KEY", "").strip()

    @property
    def tts_model(self) -> str:
        return os.getenv("TTS_MODEL", "chatterbox-v3").strip()

    @property
    def tts_configured(self) -> bool:
        return bool(self.tts_base_url and self.tts_api_key)


settings = Settings()
