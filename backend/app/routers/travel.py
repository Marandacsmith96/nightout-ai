"""Travel-time endpoint — live Google Routes when configured, labeled estimate otherwise."""
from __future__ import annotations

from fastapi import APIRouter, Query

from app.schemas import TravelEstimate
from app.services import routes

router = APIRouter(prefix="/api/travel", tags=["travel"])


@router.get("/time", response_model=TravelEstimate)
async def travel_time(
    from_lat: float = Query(..., description="Origin latitude"),
    from_lng: float = Query(..., description="Origin longitude"),
    to_lat: float = Query(..., description="Destination latitude"),
    to_lng: float = Query(..., description="Destination longitude"),
    mode: str = Query("walking", pattern="^(walking|driving|transit)$"),
) -> TravelEstimate:
    return await routes.travel_time(from_lat, from_lng, to_lat, to_lng, mode)
