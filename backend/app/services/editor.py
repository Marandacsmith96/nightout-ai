"""Itinerary editor — applies conversational changes to an existing plan.

The AI only *interprets* what the user wants (a small structured op). The
editor then applies the op deterministically:
- replace  -> a NEW candidate is retrieved for that stop's kind (filtered by
              the preference, e.g. cheaper) and the AI picks among THOSE; the
              other stops are untouched.
- add      -> new candidates retrieved for the requested kind, inserted before
              drinks/dessert.
- remove   -> that stop only is dropped.
- constraints -> budget/end/start/restrictions/transport updated, then the
              whole night is rebuilt around the new constraints.
- replan   -> full rebuild.
Every path recomputes the schedule, travel times, and budget through the same
planner helpers, so numbers stay consistent. Locked stops survive replans.
"""
from __future__ import annotations

from app.core.config import settings
from app.schemas import Itinerary, PlanRequest, Venue
from app.services import ai, catalog, planner

_CLOSE_KINDS = {"cocktail bars", "casual drinks", "dessert or coffee"}


def _stops_summary(itinerary: Itinerary) -> list[dict]:
    return [
        {"index": s.index, "kind": s.kind, "title": s.title, "cost": s.cost_per_person}
        for s in itinerary.stops
    ]


async def _pick_with_reason(
    request: PlanRequest, kind: str, preference: str, exclude_ids: set[str], cheaper_than: int | None
) -> tuple[Venue | None, str]:
    resp = await catalog.search_venues(
        query=preference or kind,
        city=request.city,
        state=request.state,
        categories=[kind],
        budget=request.budget,
        limit=6,
    )
    candidates = [v for v in resp.venues if v.id not in exclude_ids]
    if cheaper_than is not None:
        candidates = [v for v in candidates if (v.cost_estimate_per_person or 0) < cheaper_than]
    if not candidates:
        return None, f"No {kind} options fit — try a higher budget or another area."

    pick_request = request.model_dump()
    pick_request["activities"] = [kind]
    pick_request["notes"] = (
        (preference or "pick a good option") + " for the group. "
        + (f"Must be cheaper than ${cheaper_than}." if cheaper_than else "")
    )
    reason = f"Top-rated {kind} in {request.city}."
    venue = None
    if settings.openai_api_key:
        proposal, _ = await ai.propose_itinerary(pick_request, [{
            "id": v.id, "name": v.name, "address": v.address, "tags": v.tags,
            "price_estimate_per_person": v.cost_estimate_per_person, "rating": v.rating,
            "hours_verified": v.hours_verified, "source": v.source,
        } for v in candidates])
        picks = proposal.get("stops") if proposal else None
        if picks:
            vid = picks[0].get("venue_id")
            if vid in {v.id for v in candidates}:
                venue = next(v for v in candidates if v.id == vid)
                reason = picks[0].get("reason") or reason
    if venue is None:
        venue = max(candidates, key=lambda v: v.rating or 0)
    return venue, reason


async def edit_itinerary(
    request: PlanRequest,
    itinerary: Itinerary,
    instruction: str,
    locked_indices: list[int] = None,
) -> dict:
    """Apply a conversational edit. Returns {"itinerary": Itinerary, "reply": str}."""
    locked_indices = locked_indices or []
    reply = ""
    notes: list[str] = list(itinerary.edits or [])

    intent, error = await ai.interpret_edit(instruction, request.model_dump(), _stops_summary(itinerary))
    if intent is None:
        # Can't interpret: don't fabricate a change — polite no-op with the error.
        return {
            "itinerary": itinerary,
            "reply": (
                "I couldn't quite understand that request right now "
                f"({error}). Try phrasing it like \u201CMake dinner cheaper\u201D or "
                "\u201Cwe want to finish by 10 PM\u201D."
            ),
        }
    if intent["op"] == "none":
        return {"itinerary": itinerary, "reply": intent["reply"] or "Got it — nothing to change!"}

    used_ids = {s.venue.id for s in itinerary.stops if s.venue}
    stops_list = list(itinerary.stops)

    if intent["op"] == "constraints":
        updated = request.model_dump()
        c = intent["constraints"]
        if c.get("budget"):
            updated["budget"] = int(c["budget"])
        if c.get("end_time"):
            updated["end_time"] = c["end_time"]
        if c.get("start_time"):
            updated["start_time"] = c["start_time"]
        if c.get("restrictions"):
            updated["restrictions"] = c["restrictions"]
        if c.get("transport"):
            updated["transport"] = c["transport"]
        new_req = PlanRequest(**updated)
        changed_restrictions = (
            c.get("restrictions") is not None
            and c["restrictions"] != request.restrictions
        )
        if changed_restrictions:
            # Dietary changes affect venue CHOICE -> rebuild picks around them.
            return await replan(
                new_req, itinerary, locked_indices,
                note="Updated your dietary constraints and rebuilt the picks to fit.",
            )
        # Time / budget / transport changes affect the SCHEDULE -> keep the
        # same venues and re-schedule them (preserving what wasn't asked to change).
        return await _rebuild(
            new_req, list(itinerary.stops),
            list(itinerary.edits or []) + ["Updated constraints (per your request)."],
            reply=intent["reply"] or "Updated the plan around your new constraints.",
        )

    if intent["op"] == "replan":
        return await replan(request, itinerary, locked_indices,
                            note=intent["preference"] or "Replanned the whole night.")

    if intent["op"] == "remove":
        idx = intent["index"]
        if 0 <= idx < len(stops_list):
            dropped = stops_list.pop(idx)
            return await _rebuild(request, stops_list, notes + [f"Removed {dropped.title} (per your request)."],
                                  reply=intent["reply"] or f"Removed the {dropped.kind} stop.")
        return {"itinerary": itinerary, "reply": "I couldn't find that stop to remove."}

    if intent["op"] == "replace":
        idx = intent["index"]
        if not (0 <= idx < len(stops_list)):
            return {"itinerary": itinerary, "reply": "I couldn't find the stop you meant."}
        target = stops_list[idx]
        kind = intent["kind"] or target.kind
        cheaper_than = (
            target.cost_per_person
            if "cheap" in (intent["preference"].lower() + instruction.lower())
            else None
        )
        venue, reason = await _pick_with_reason(
            request, kind, intent["preference"], used_ids, cheaper_than
        )
        if venue is None:
            return {
                "itinerary": itinerary,
                "reply": f"No suitable {kind} found — try a higher budget or a different preference.",
            }
        stops_list[idx] = target.model_copy(update={
            "kind": kind, "title": venue.name, "venue": venue,
            "note": reason, "cost_per_person": venue.cost_estimate_per_person,
            "cost_verified": venue.price_verified,
        })
        return await _rebuild(request, stops_list,
                              notes + [f"{target.title} \u2192 {venue.name} (per your request)."],
                              reply=intent["reply"] or f"Swapped {target.title} for {venue.name}.")

    if intent["op"] == "add":
        kind = intent["kind"]
        if not kind or kind not in planner.KIND_DURATION_MIN:
            return {"itinerary": itinerary, "reply": "I'm not sure what activity to add."}
        venue, reason = await _pick_with_reason(request, kind, intent["preference"], used_ids, None)
        if venue is None:
            return {"itinerary": itinerary, "reply": f"No {kind} options found — try another activity."}
        insert_at = len(stops_list)
        for i, s in enumerate(stops_list):
            if s.kind in _CLOSE_KINDS:
                insert_at = i
                break
        stop = itinerary.stops[0].model_copy(update={
            "index": 0, "kind": kind, "title": venue.name, "venue": venue,
            "note": reason, "travel_from_previous_min": None,
            "travel_from_previous_mode": None, "travel_from_previous_source": None,
            "cost_per_person": venue.cost_estimate_per_person, "cost_verified": venue.price_verified,
        })
        stops_list.insert(insert_at, stop)
        return await _rebuild(request, stops_list,
                              notes + [f"Added a {kind} stop: {venue.name}."],
                              reply=intent["reply"] or f"Added {venue.name} for {kind}.")

    return {"itinerary": itinerary, "reply": "Got it!"}


async def replan(
    request: PlanRequest, itinerary: Itinerary, locked_indices: list[int], note: str = ""
) -> dict:
    """Rebuild the night from scratch, then force locked stops back in place."""
    locked = [s for i, s in enumerate(itinerary.stops) if i in locked_indices]
    fresh = await planner.generate(request)
    if locked:
        pools = {}
        for s in locked:
            if s.venue:
                pools[s.venue.id] = s.venue
        for s in fresh.stops:
            if s.venue:
                pools[s.venue.id] = s.venue
        picks = []
        locked_iter = iter(locked)
        for s in fresh.stops:
            locked_stop = next(locked_iter, None)
            if locked_stop and locked_stop.venue:
                picks.append({"kind": locked_stop.kind, "venue_id": locked_stop.venue.id,
                              "reason": "Locked by the group."})
            elif s.venue:
                picks.append({"kind": s.kind, "venue_id": s.venue.id, "reason": s.note})
        stops, notes = await planner.compute_stops(request, picks, pools)
        budget = planner.trim_to_budget(request, stops, notes)
        fresh = fresh.model_copy(update={
            "stops": stops, "budget": budget,
            "edits": (fresh.edits or []) + ([note] if note else []) + notes,
            "id": __import__("uuid").uuid4().hex[:8],
        })
    return {"itinerary": fresh, "reply": note or "Rebuilt your night — locked stops stayed put."}


async def _rebuild(
    request: PlanRequest, stops_list: list, notes: list[str], reply: str
) -> dict:
    """Recompute schedule + budget for a manually edited stop list."""
    pools = {}
    for s in stops_list:
        if s.venue:
            pools[s.venue.id] = s.venue
    picks = [{"kind": s.kind, "venue_id": s.venue.id, "reason": s.note} for s in stops_list if s.venue]
    stops, new_notes = await planner.compute_stops(request, picks, pools)
    budget = planner.trim_to_budget(request, stops, notes + new_notes)
    itinerary = Itinerary(
        id=__import__("uuid").uuid4().hex[:8],
        city=request.city,
        date=request.date,
        stops=stops,
        budget=budget,
        generated_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(timespec="seconds"),
        demo=settings.demo_mode,
        demo_note=("Sample venues used — connect Google Places for live results." if settings.demo_mode else "Live Google Places results."),
        edits=notes + new_notes,
    )
    return {"itinerary": itinerary, "reply": reply}
