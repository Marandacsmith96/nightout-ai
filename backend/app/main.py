"""NightOut AI — backend entry point.

Phase 2 adds the venue-retrieval and travel-time endpoints; Phase 3 will add
itinerary generation on top of these services.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import plan, travel, venues

app = FastAPI(
    title="NightOut AI API",
    version="0.3.0",
    description="Backend for the NightOut AI night-out planner.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(venues.router)
app.include_router(travel.router)
app.include_router(plan.router)


@app.get("/api/health")
def health() -> dict:
    """Liveness check used by the frontend and by tests."""
    return {
        "status": "ok",
        "app": "NightOut AI",
        "version": "0.3.0",
        "demo_mode": settings.demo_mode,
        "ai_configured": bool(settings.openai_api_key),
        "demo_mode_note": (
            "No Google Places key configured — venue retrieval runs in "
            "explicitly-labeled demo mode with sample places."
            if settings.demo_mode
            else "Live venue retrieval configured."
        ),
    }
