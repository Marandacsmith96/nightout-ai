"""Venue catalog: the single entry point the rest of the app uses.

- Live mode (Google Places key configured)  -> real searches, enriched details.
- Demo mode (no key)                        -> clearly-labeled sample catalog.
Never mixes the two; every response carries its `source`.
"""
from __future__ import annotations

from app.core.config import settings
from app.schemas import Venue, VenueSearchResponse
from app.services import demo_data, places

# Normalize a free-text city into our demo catalog key (e.g. "Denver, CO" -> "denver").
_KNOWN_CITIES = {
    "denver": "denver",
    "denver, co": "denver",
    "boulder": "boulder",
    "boulder, co": "boulder",
    "austin": "austin",
    "austin, tx": "austin",
}


def _demo_city_key(city: str) -> str | None:
    return _KNOWN_CITIES.get((city or "").strip().lower())


async def search_venues(
    query: str,
    city: str,
    state: str = "",
    categories: list[str] | None = None,
    budget: int | None = None,
    limit: int = 8,
) -> VenueSearchResponse:
    """Search venues for a planned night. Live when configured, demo otherwise."""
    if settings.demo_mode:
        return _demo_search(query, city, categories or [], budget, limit)

    # -- live Google Places path --
    search_query = query.strip() or ("restaurants bars activities")
    if city.strip():
        search_query += f" in {city.strip()}{', ' + state.strip() if state.strip() else ''}"
    try:
        venues = await places.search_live(search_query, limit=limit)
    except Exception as exc:  # noqa: BLE001 — surface a readable message, never crash
        return VenueSearchResponse(
            query=query, city=city, source="error", source_label="Google Places request failed",
            note=f"Venue search failed ({exc}). Please check GOOGLE_PLACES_API_KEY and try again.",
            venues=[],
        )
    if not venues:
        return VenueSearchResponse(
            query=query, city=city, source="google_places",
            source_label="Live Google Places result", note="No venues matched. Try a different area or category.",
            venues=[],
        )
    return VenueSearchResponse(
        query=query, city=city, source="google_places",
        source_label="Live Google Places result", venues=venues,
    )


def _demo_search(query: str, city: str, categories: list[str], budget: int | None, limit: int) -> VenueSearchResponse:
    key = _demo_city_key(city)
    if key is None:
        return VenueSearchResponse(
            query=query, city=city, source="demo",
            source_label="Demo sample places",
            note=(
                f"No sample venues for \u201c{city}\u201d yet — the demo catalog covers "
                f"{', '.join(demo_data.demo_cities())}. Add a Google Places API key for any city."
            ),
            venues=[],
        )
    venues = demo_data.search_demo(key, categories, budget, limit)
    return VenueSearchResponse(
        query=query, city=city, source="demo",
        source_label="Demo sample places — not live results",
        note="Demo mode: sample venues labeled as such. Add GOOGLE_PLACES_API_KEY for live results.",
        venues=venues,
    )
