"""Travel-time estimation between stops.

Live mode uses the Google Routes API when GOOGLE_ROUTES_API_KEY is set.
Otherwise we estimate walking time from a straight-line distance
(great-circle), and label every estimate as such. Estimates are fine for
planning; the UI always shows which source produced the number.
"""
from __future__ import annotations

import math

import httpx

from app.core.config import settings
from app.schemas import TravelEstimate

_EARTH_RADIUS_M = 6_371_000.0
_WALK_SPEED_MS = 1.35  # ~3 mph


def _great_circle_m(lat1: float, lng1: float, lat2: float, lng2: float) -> int:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return int(2 * _EARTH_RADIUS_M * math.asin(math.sqrt(a)))


def _mode_to_route_mode(mode: str) -> str:
    return {"walking": "WALK", "driving": "DRIVE", "transit": "TRANSIT"}.get(mode, "WALK")


async def _routes_api(lat1, lng1, lat2, lng2, mode: str) -> TravelEstimate | None:
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://routes.googleapis.com/directions/v2:computeRoutes",
                headers={
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": settings.google_routes_api_key,
                    "X-Goog-FieldMask": "routes.distanceMeters,routes.duration",
                },
                json={
                    "origin": {"location": {"latLng": {"latitude": lat1, "longitude": lng1}}},
                    "destination": {"location": {"latLng": {"latitude": lat2, "longitude": lng2}}},
                    "travelMode": _mode_to_route_mode(mode),
                },
                timeout=8.0,
            )
        if resp.status_code != 200:
            return None
        body = resp.json()
        routes = body.get("routes") or []
        if not routes:
            return None
        d_m = int(routes[0].get("distanceMeters", 0))
        duration_s = float((routes[0].get("duration") or "0s").rstrip("s"))
        return TravelEstimate(
            mode=mode,
            distance_m=d_m,
            duration_min=max(1, round(duration_s / 60)),
            source="google_routes",
            source_label="Live Google Routes result",
        )
    except httpx.HTTPError:
        return None


def estimate_duration_min(distance_m: int, mode: str) -> int:
    # duration in minutes = distance / speed(m/s) / 60
    if mode == "driving":
        return max(1, round(distance_m / 13.0 / 60))  # ~13 m/s city driving incl. lights
    if mode == "transit":
        return max(1, round(distance_m / 7.0 / 60))  # slower, includes waiting
    return max(1, round(distance_m / (_WALK_SPEED_MS * 60)))


async def travel_time(lat1: float, lng1: float, lat2: float, lng2: float, mode: str = "walking") -> TravelEstimate:
    """Best available travel estimate: live Routes when configured, else labeled estimate."""
    if settings.google_routes_api_key:
        live = await _routes_api(lat1, lng1, lat2, lng2, mode)
        if live:
            return live
    dist = _great_circle_m(lat1, lng1, lat2, lng2)
    # Straight-line is optimistic; inflate by 1.25x for real street paths.
    dist_realistic = int(dist * 1.25)
    return TravelEstimate(
        mode=mode,
        distance_m=dist_realistic,
        duration_min=estimate_duration_min(dist_realistic, mode),
        source="estimated",
        source_label="Estimated from straight-line distance (no Routes key)",
    )
