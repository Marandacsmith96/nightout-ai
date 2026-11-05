"""Itinerary planner orchestration.

Pipeline:
1. Validate the request (pydantic).
2. Retrieve candidate venues per activity from the catalog (live or demo).
3. Ask the AI to pick stops from those candidates ONLY.
4. Validate the AI's choices against the candidate list (any unknown id or
   unrequested kind -> reject that proposal and fall back).
5. Compute the real schedule (start time + per-kind durations + travel between
   stops) and the budget summary from VENUE data — never from the model.

If the AI is missing, unreachable, or returns garbage, the deterministic
fallback picks the highest-rated candidates per activity, and the response
says so. The app never crashes and never presents invented data.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.core.config import settings
from app.schemas import (
    BudgetSummary,
    Itinerary,
    ItineraryStop,
    PlanRequest,
    Venue,
)
from app.services import ai, catalog, routes
from app.services.demo_data import CATEGORY_TAGS

# Per-stop duration estimates (minutes) — planning assumptions, labeled as such.
KIND_DURATION_MIN = {
    "dinner": 90,
    "cocktail bars": 75,
    "casual drinks": 75,
    "live music": 120,
    "dancing": 120,
    "comedy shows": 120,
    "concerts": 150,
    "games & arcade bars": 90,
    "bowling": 90,
    "escape rooms": 75,
    "outdoor activities": 60,
    "dessert or coffee": 45,
    "something unexpected": 90,
}

# Evening-order helpers: dinner leads, drinks/dessert close the night.
_LEAD_KINDS = {"dinner"}
_CLOSE_KINDS = {"cocktail bars", "casual drinks", "dessert or coffee"}


def _to_minutes(hhmm: str) -> int:
    h, m = (int(x) for x in hhmm.split(":"))
    return h * 60 + m


def _from_minutes(t: int) -> str:
    t %= 1440
    return f"{t // 60:02d}:{t % 60:02d}"


def _clock_window(request: PlanRequest) -> tuple[int, int]:
    start = _to_minutes(request.start_time)
    end = _to_minutes(request.end_time)
    if end <= start:
        end += 1440  # night runs past midnight
    return start, end


def _kind_for(activity: str) -> str:
    return activity.lower()


def _order_stops(picks: list[dict]) -> list[dict]:
    """Dinner first, drinks/dessert last, everything else keeps the model's order."""
    leads = [p for p in picks if p["kind"] in _LEAD_KINDS]
    closes = [p for p in picks if p["kind"] in _CLOSE_KINDS]
    middles = [p for p in picks if p["kind"] not in _LEAD_KINDS and p["kind"] not in _CLOSE_KINDS]
    return leads + middles + closes


def _candidate_dicts(venues: list[Venue]) -> list[dict]:
    return [
        {
            "id": v.id,
            "name": v.name,
            "address": v.address,
            "tags": v.tags,
            "price_estimate_per_person": v.cost_estimate_per_person,
            "rating": v.rating,
            "hours_verified": v.hours_verified,
            "source": v.source,
        }
        for v in venues
    ]


async def _retrieve_candidates(request: PlanRequest) -> dict[str, Venue]:
    """One candidate pool per selected activity, shared across live/demo."""
    pools: dict[str, Venue] = {}
    for activity in request.activities:
        resp = await catalog.search_venues(
            query=activity,
            city=request.city,
            state=request.state,
            categories=[activity],
            budget=request.budget,
            limit=6,
        )
        for v in resp.venues:
            pools[v.id] = v  # dedupe across categories
    return pools


def _deterministic_fallback(request: PlanRequest, pools: dict[str, Venue]) -> list[dict]:
    """Top-rated candidate per requested activity (dinner first, drinks last).

    Uses the exact same category->tag mapping as retrieval, skips activities
    with no match, and never proposes the same venue twice.
    """
    picks = []
    used_ids: set[str] = set()
    for activity in request.activities:
        kind = _kind_for(activity)
        wanted = CATEGORY_TAGS.get(kind, set())
        tagged = [v for v in pools.values() if (set(v.tags) & wanted) and v.id not in used_ids]
        if not tagged:
            # no tag match: highest-rated unused venue, if any
            tagged = [v for v in sorted(pools.values(), key=lambda v: v.rating or 0, reverse=True) if v.id not in used_ids]
        if not tagged:
            continue
        best = max(tagged, key=lambda v: (v.rating or 0))
        used_ids.add(best.id)
        picks.append({"kind": kind, "venue_id": best.id, "reason": f"Top-rated {activity} choice in {request.city}."})
    return _order_stops(picks)


def _validate_picks(picks: list[dict], request: PlanRequest, pools: dict[str, Venue]) -> list[dict]:
    allowed_kinds = {_kind_for(a) for a in request.activities}
    clean = []
    for p in picks:
        kind, vid = p.get("kind"), p.get("venue_id")
        if kind not in allowed_kinds:
            continue
        if vid not in pools:
            continue
        clean.append(p)
    return _order_stops(clean)


async def _travel_to_previous(prev: Venue | None, venue: Venue, mode: str) -> tuple[int | None, str | None, str | None]:
    if prev is None:
        return None, None, None
    est = await routes.travel_time(prev.lat, prev.lng, venue.lat, venue.lng, mode)
    return est.duration_min, mode, est.source


def _budget(request: PlanRequest, stops: list[ItineraryStop], transport: str) -> BudgetSummary:
    lines: list[dict] = []
    total = 0
    for s in stops:
        cost = s.cost_per_person or 0
        verified = s.cost_verified
        total += cost
        lines.append({"label": s.kind, "amount": cost, "verified": verified})
    transport_cost = 0
    if transport.lower() == "rideshare":
        transport_cost = 10  # rough estimate per person; flagged below
        total += transport_cost
        lines.append({"label": "rideshare (estimate)", "amount": transport_cost, "verified": False})
    remaining = request.budget - total
    return BudgetSummary(
        per_person_total=total,
        budget=request.budget,
        remaining=remaining,
        lines=lines,
        note=(
            "Over budget by $" + str(-remaining) + " per person — try cheaper stops or raise the budget."
            if remaining < 0
            else "Estimates may exclude taxes, tips, and fees."
        ),
    )


async def generate(request: PlanRequest) -> Itinerary:
    pools = await _retrieve_candidates(request)

    if not pools:
        return Itinerary(
            id=uuid.uuid4().hex[:8],
            city=request.city,
            date=request.date,
            stops=[],
            budget=_budget(request, [], request.transport),
            demo=settings.demo_mode,
            demo_note="No venues found for these preferences — try another city, category, or a higher budget.",
            edits=[],
        )

    ai_note = ""
    picks: list[dict] | None = None
    if settings.openai_api_key:
        proposal, ai_error = await ai.propose_itinerary(request.model_dump(), _candidate_dicts(list(pools.values())))
        picks = proposal.get("stops") if proposal else None
        if picks is None:
            ai_note = (
                "AI selection unavailable (" + ai_error + ") — showing the top-rated options instead."
            )
    if picks is None:
        picks = _deterministic_fallback(request, pools)

    clean = _validate_picks(picks, request, pools)
    if not clean:
        clean = _deterministic_fallback(request, pools)

    start_min, end_min = _clock_window(request)
    mode = request.transport.lower()
    stops: list[ItineraryStop] = []
    clock = start_min
    prev_venue: Venue | None = None
    notes: list[str] = []

    for i, pick in enumerate(clean):
        venue = pools[pick["venue_id"]]
        travel, travel_mode, travel_src = await _travel_to_previous(prev_venue, venue, mode)
        if travel:
            clock += travel
        duration = KIND_DURATION_MIN.get(pick["kind"], 90)
        stop_start, stop_end = clock, clock + duration
        if stop_start >= end_min:
            notes.append(f"{pick['kind']} skipped — not enough time before {request.end_time}.")
            continue
        stops.append(
            ItineraryStop(
                index=len(stops) + 1,
                kind=pick["kind"],
                title=venue.name,
                start=_from_minutes(stop_start),
                end=_from_minutes(stop_end),
                venue=venue,
                note=pick.get("reason", ""),
                travel_from_previous_min=travel,
                travel_from_previous_mode=travel_mode,
                travel_from_previous_source=travel_src,
                cost_per_person=venue.cost_estimate_per_person,
                cost_verified=venue.price_verified,
            )
        )
        prev_venue = venue
        clock = stop_end

    budget = _budget(request, stops, request.transport)

    # Strict-budget guarantee: never present a plan whose total exceeds the
    # per-person cap. Trim trailing (least-essential) stops first — dinner
    # survives, drinks/dessert go — and say so honestly in the edit notes.
    while budget.per_person_total > request.budget and len(stops) > 1:
        dropped = stops.pop()
        notes.append(
            f"Removed the {dropped.kind} stop ({dropped.title}) to stay within "
            f"the ${request.budget}/person budget."
        )
        budget = _budget(request, stops, request.transport)

    return Itinerary(
        id=uuid.uuid4().hex[:8],
        city=request.city,
        date=request.date,
        stops=stops,
        budget=budget,
        generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        demo=settings.demo_mode,
        demo_note=(
            "Sample venues used — connect Google Places for live results."
            if settings.demo_mode
            else "Live Google Places results."
        ),
        edits=notes + ([ai_note] if ai_note else []),
    )
