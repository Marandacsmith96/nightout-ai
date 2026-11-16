"""Regression scenarios found during the final requirements review."""
import asyncio

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import PlanRequest
from app.services import ai, editor, planner

REQUEST = dict(city="Denver", date="2026-12-05", group_size=4, budget=60,
               start_time="18:00", end_time="23:30",
               activities=["Dinner", "Games & arcade bars", "Casual drinks"])


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setenv("GOOGLE_PLACES_API_KEY", "")
    monkeypatch.setenv("GOOGLE_ROUTES_API_KEY", "")
    from app.core.config import _has_places_key
    _has_places_key.cache_clear()
    yield
    _has_places_key.cache_clear()


@pytest.mark.parametrize("budget", [5, 15, 25])
def test_rideshare_never_exceeds_budget(budget):
    result = TestClient(app).post("/api/plan/generate", json={
        **REQUEST, "budget": budget, "activities": ["Dinner"], "transport": "Rideshare",
    }).json()
    assert result["budget"]["per_person_total"] <= budget
    if not result["stops"]:
        assert result["budget"]["per_person_total"] == 0


@pytest.mark.parametrize("indices", [[1], [0, 1]])
def test_regenerate_preserves_locks_without_duplicates(indices):
    async def scenario():
        req = PlanRequest(**REQUEST)
        original = await planner.generate(req)
        result = (await editor.replan(req, original, indices))["itinerary"]
        ids = [s.venue.id for s in result.stops]
        assert len(ids) == len(set(ids))
        for i in indices:
            assert result.stops[i].venue.id == original.stops[i].venue.id
    asyncio.run(scenario())


def test_infeasible_lock_explained():
    async def scenario():
        req = PlanRequest(**REQUEST)
        original = await planner.generate(req)
        result = (await editor.replan(req.model_copy(update={"budget": 5}), original, [0]))["itinerary"]
        assert result.budget.per_person_total <= 5
        assert any("Could not retain locked stop" in n for n in result.edits)
    asyncio.run(scenario())


def test_sequential_edits_return_updated_preferences(monkeypatch):
    intents = iter([
        {"op": "constraints", "constraints": {"start_time": "19:00", "budget": 50, "transport": "Driving", "restrictions": []}},
        {"op": "replace", "index": 0, "kind": "dinner", "preference": "different"},
    ])
    async def interpret(*args):
        return {"reply": "Updated", **next(intents)}, ""
    monkeypatch.setattr(ai, "interpret_edit", interpret)
    client = TestClient(app)
    original = client.post("/api/plan/generate", json=REQUEST).json()
    first = client.post("/api/plan/edit", json={
        "instruction": "Start at 7 PM", "request": REQUEST, "itinerary": original,
    }).json()["itinerary"]
    second = client.post("/api/plan/edit", json={
        "instruction": "Swap dinner", "request": first["request"], "itinerary": first,
    }).json()["itinerary"]
    assert second["request"]["start_time"] == "19:00"
    assert second["request"]["budget"] == 50
    assert second["request"]["transport"] == "Driving"
    assert second["stops"][0]["start"] == "19:00"


def test_ai_duplicate_picks_rejected():
    picks = [{"kind": "dinner", "venue_id": "den-01", "reason": "test"}] * 2
    assert len(planner._validate_picks(picks, PlanRequest(**REQUEST), {"den-01": None})) == 1


def test_unknown_cost_is_not_treated_as_free():
    async def scenario():
        req = PlanRequest(**REQUEST)
        itinerary = await planner.generate(req)
        stops = [itinerary.stops[0].model_copy(update={"cost_per_person": None})]
        notes = []
        planner.trim_to_budget(req, stops, notes)
        assert not stops
        assert any("cost is unknown" in n for n in notes)
    asyncio.run(scenario())


def test_add_to_empty_itinerary_does_not_crash(monkeypatch):
    async def interpret(*args):
        return {"op": "add", "kind": "dessert or coffee", "preference": "", "reply": "Added dessert"}, ""
    monkeypatch.setattr(ai, "interpret_edit", interpret)
    async def scenario():
        req = PlanRequest(**{**REQUEST, "activities": []})
        empty = await planner.generate(req)
        assert not empty.stops
        result = await editor.edit_itinerary(req, empty, "Add dessert")
        assert result["itinerary"].stops
    asyncio.run(scenario())
