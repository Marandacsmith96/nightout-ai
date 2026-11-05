"""Editor tests — the AI interpretation is stubbed; the deterministic apply
logic is what we exercise (swap/remove/constraints/locks)."""
import pytest

from app.schemas import PlanRequest
from app.services import ai, editor, planner

DENVER_REQUEST = PlanRequest(**{
    "city": "Denver", "date": "2026-12-05", "group_size": 4, "budget": 60,
    "start_time": "18:00", "end_time": "23:30",
    "activities": ["Dinner", "Games & arcade bars", "Casual drinks"],
    "atmosphere": "Casual & relaxed", "transport": "Walking",
    "distance": "Moderate travel between stops is okay", "notes": "",
})


@pytest.fixture()
def stub_ai(monkeypatch):
    """No live AI in tests: deterministic fallback everywhere, canned intents."""

    async def fake_propose(request, candidates):
        return None, "stubbed"

    async def fake_interpret(instruction, request, stops):
        return None, "stubbed"

    monkeypatch.setattr(ai, "propose_itinerary", fake_propose)
    monkeypatch.setattr(ai, "interpret_edit", fake_interpret)
    return ai


@pytest.fixture()
async def base_itinerary():
    return await planner.generate(DENVER_REQUEST)


def test_edit_remove_stop(stub_ai):
    itinerary = asyncio_run(planner.generate(DENVER_REQUEST))
    n = len(itinerary.stops)
    result = asyncio_run(editor.edit_itinerary(
        DENVER_REQUEST, itinerary, "Remove the second stop"))
    # interpret is stubbed -> polite no-op, unchanged
    assert result["itinerary"].id == itinerary.id
    assert len(result["itinerary"].stops) == n


def test_remove_op_applied_directly(stub_ai):
    itinerary = asyncio_run(planner.generate(DENVER_REQUEST))
    assert len(itinerary.stops) >= 2
    stops_list = list(itinerary.stops)
    dropped = stops_list.pop(1)
    result = asyncio_run(editor._rebuild(DENVER_REQUEST, stops_list, ["removed " + dropped.title], "Done."))
    rebuilt = result["itinerary"]
    assert len(rebuilt.stops) == len(stops_list)
    assert all(s.venue.id != dropped.venue.id for s in rebuilt.stops)
    # schedule still valid: non-decreasing times
    times = [s.start for s in rebuilt.stops]
    assert times == sorted(times)


def test_replace_cheaper_filter(stub_ai):
    itinerary = asyncio_run(planner.generate(DENVER_REQUEST))
    dinner = next(s for s in itinerary.stops if s.kind == "dinner")
    # Cheaper-than filter with a ceiling ABOVE the picked dinner: every option
    # returned must be under the ceiling.
    ceiling = (dinner.cost_per_person or 10) + 10
    venue, reason = asyncio_run(editor._pick_with_reason(
        DENVER_REQUEST, "dinner", "cheaper", {dinner.venue.id}, ceiling))
    assert venue is not None
    assert (venue.cost_estimate_per_person or 0) < ceiling
    assert venue.id != dinner.venue.id


def test_replan_preserves_locked_stop(stub_ai):
    itinerary = asyncio_run(planner.generate(DENVER_REQUEST))
    assert len(itinerary.stops) >= 1
    locked_venue_id = itinerary.stops[0].venue.id
    result = asyncio_run(editor.replan(DENVER_REQUEST, itinerary, [0], "Replan"))
    new_it = result["itinerary"]
    assert new_it.stops[0].venue.id == locked_venue_id


def test_budget_invariant_after_rebuild(stub_ai):
    itinerary = asyncio_run(planner.generate(DENVER_REQUEST))
    stops_list = list(itinerary.stops)[:2]
    result = asyncio_run(editor._rebuild(DENVER_REQUEST, stops_list, [], "ok"))
    assert result["itinerary"].budget.per_person_total <= DENVER_REQUEST.budget


def asyncio_run(coro):
    import asyncio
    return asyncio.run(coro)
