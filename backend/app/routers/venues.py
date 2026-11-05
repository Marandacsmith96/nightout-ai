"""Venue search endpoint — live Google Places when configured, demo otherwise."""
from __future__ import annotations

from fastapi import APIRouter, Query

from app.schemas import VenueSearchResponse
from app.services import catalog

router = APIRouter(prefix="/api/venues", tags=["venues"])


@router.get("/search", response_model=VenueSearchResponse)
async def search_venues(
    query: str = Query("", description="Free-text search, e.g. 'dinner' or 'arcade bar'"),
    city: str = Query("", description="City name, e.g. 'Denver'"),
    state: str = Query("", description="State abbreviation, e.g. 'CO' (optional)"),
    budget: int | None = Query(None, ge=0, description="Max $ per person (optional filter)"),
    limit: int = Query(8, ge=1, le=20),
) -> VenueSearchResponse:
    return await catalog.search_venues(
        query=query,
        city=city,
        state=state,
        categories=[query] if query else None,
        budget=budget,
        limit=limit,
    )
