"""Google Places API client (live mode).

Text Search finds candidates; Place Details enriches the top few with
opening hours, ratings, price level, and photo references. Everything is
normalized into the shared `Venue` schema with explicit verification flags.
"""
from __future__ import annotations

import httpx

from app.core.config import settings
from app.schemas import Venue

_PLACES_BASE = "https://maps.googleapis.com/maps/api/place"
_DETAIL_FIELDS = "place_id,name,formatted_address,geometry,rating,user_ratings_total,price_level,opening_hours,photos,website"
_TIMEOUT = 8.0


def _maps_url(name: str, address: str) -> str:
    q = f"{name} {address}".replace(" ", "+")
    return f"https://www.google.com/maps/search/?api=1&query={q}"


def _price_per_person(price_level: int | None) -> int | None:
    return {0: None, 1: 12, 2: 25, 3: 45, 4: 90}.get(price_level or 0)


def _normalize(item: dict, enriched: dict | None, idx: int) -> Venue:
    """Map a Places API result (and optional details) onto our schema."""
    geom = (item.get("geometry") or {}).get("location") or {}
    photo_ref = None
    photos = (enriched or item).get("photos") or []
    if photos and isinstance(photos[0], dict):
        photo_ref = photos[0].get("photo_reference")
    hours = None
    if enriched and enriched.get("opening_hours"):
        hours = enriched["opening_hours"].get("weekday_text") or None
    name = item.get("name") or "Untitled place"
    address = (enriched or item).get("formatted_address") or ""
    return Venue(
        id=item.get("place_id") or f"gpl-{idx}",
        name=name,
        address=address,
        lat=float(geom.get("lat", 0.0)),
        lng=float(geom.get("lng", 0.0)),
        rating=item.get("rating"),
        rating_verified=True,
        price_level=item.get("price_level"),
        price_verified=True,
        cost_estimate_per_person=_price_per_person(item.get("price_level")),
        hours=hours,
        hours_verified=bool(hours),
        photo_reference=photo_ref,
        google_maps_url=_maps_url(name, address),
        source="google_places",
        source_label="Live Google Places result",
    )


async def _text_search(query: str, client: httpx.AsyncClient) -> list[dict]:
    url = f"{_PLACES_BASE}/textsearch/json"
    resp = await client.get(
        url,
        params={"query": query, "key": settings.google_places_api_key},
        timeout=_TIMEOUT,
    )
    body = resp.json()
    if body.get("status") not in ("OK", "ZERO_RESULTS"):
        raise RuntimeError(f"Google Places textsearch failed: {body.get('status')} {body.get('error_message', '')}")
    return body.get("results", [])


async def _place_details(place_id: str, client: httpx.AsyncClient) -> dict | None:
    url = f"{_PLACES_BASE}/details/json"
    resp = await client.get(
        url,
        params={"place_id": place_id, "fields": _DETAIL_FIELDS, "key": settings.google_places_api_key},
        timeout=_TIMEOUT,
    )
    body = resp.json()
    if body.get("status") != "OK":
        return None
    return body.get("result")


async def search_live(query: str, limit: int = 6) -> list[Venue]:
    """Search Google Places for a category in a city, enrich the top results."""
    async with httpx.AsyncClient() as client:
        results = await _text_search(query, client)
        venues: list[Venue] = []
        for i, item in enumerate(results[:limit]):
            enriched = None
            if item.get("place_id"):
                try:
                    enriched = await _place_details(item["place_id"], client)
                except httpx.HTTPError:
                    enriched = None  # details are a bonus; search result still works
            venues.append(_normalize(item, enriched, i))
        return venues
