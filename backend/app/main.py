"""NightOut AI — backend entry point (Phase 1).

Phase 1 provides the API skeleton: health check + CORS. Real endpoints
(itinerary generation, venue retrieval, itinerary edits) arrive in
Phases 2–4.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(
    title="NightOut AI API",
    version="0.1.0",
    description="Backend for the NightOut AI night-out planner.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    """Liveness check used by the frontend and by tests."""
    return {
        "status": "ok",
        "app": "NightOut AI",
        "version": "0.1.0",
        "demo_mode": settings.demo_mode,
        "demo_mode_note": (
            "No Google Places key configured — venue retrieval runs in "
            "explicitly-labeled demo mode with sample places."
            if settings.demo_mode
            else "Live venue retrieval configured."
        ),
    }
