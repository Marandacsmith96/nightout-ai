"""Itinerary generation endpoint (Phase 3)."""
from __future__ import annotations

from fastapi import APIRouter

from app.schemas import Itinerary, PlanRequest
from app.services import planner

router = APIRouter(prefix="/api/plan", tags=["plan"])


@router.post("/generate", response_model=Itinerary)
async def generate_itinerary(request: PlanRequest) -> Itinerary:
    return await planner.generate(request)
