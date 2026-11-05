"""Planner logic tests — schedule math, validation, deterministic fallback.

The live AI call is NOT exercised here (no network in CI); instead we test the
layers that guarantee correctness regardless of what the model returns.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import PlanRequest
from app.services import planner

client = TestClient(app)

DENVER_REQUEST = {
    "city": "Denver",
    "date": "2026-12-05",
    "group_size": 6,
    "budget": 60,
    "start_time": "18:00",
    "end_time": "23:30",
    "activities": ["Dinner", "Games & arcade bars", "Casual drinks"],
    "atmosphere": "Casual & relaxed",
    "transport": "Walking",
    "distance": "Moderate travel between stops is okay",
    "notes": "",
}


def test_clock_window_past_midnight():
    req = PlanRequest(**{**DENVER_REQUEST, "start_time": "21:00", "end_time": "01:00"})
    start, end = planner._clock_window(req)
    assert start == 21 * 60
    assert end == 25 * 60  # 1:00 AM next day


def test_validate_picks_rejects_unknown_venue_ids():
    req = PlanRequest(**DENVER_REQUEST)
    pools = {"den-01": None, "den-15": None}  # type: ignore[dict-item]
    picks = [
        {"kind": "dinner", "venue_id": "den-01", "reason": "ok"},
        {"kind": "dinner", "venue_id": "evil-las-vegas-casino", "reason": "invented!"},
        {"kind": "dancing", "venue_id": "den-15", "reason": "not requested"},
    ]
    clean = planner._validate_picks(picks, req, pools)  # type: ignore[arg-type]
    assert len(clean) == 1
    assert clean[0]["venue_id"] == "den-01"


def test_order_leads_dinner_and_closes_drinks():
    picks = [
        {"kind": "casual drinks", "venue_id": "x", "reason": ""},
        {"kind": "games & arcade bars", "venue_id": "y", "reason": ""},
        {"kind": "dinner", "venue_id": "z", "reason": ""},
    ]
    ordered = planner._order_stops(picks)
    assert [p["kind"] for p in ordered] == ["dinner", "games & arcade bars", "casual drinks"]


def test_generate_demo_endpoint_returns_valid_itinerary():
    r = client.post("/api/plan/generate", json={**DENVER_REQUEST, "budget": 25})
    assert r.status_code == 200
    body = r.json()
    assert body["demo"] is True
    assert len(body["stops"]) >= 1
    for stop in body["stops"]:
        assert stop["venue"] is not None
        assert stop["venue"]["source"] == "demo"
        # cost never exceeds the per-person cap
        assert (stop["cost_per_person"] or 0) <= 25
    assert body["budget"]["per_person_total"] <= 25


@pytest.mark.asyncio
async def test_deterministic_fallback_respects_budget():
    req = PlanRequest(**{**DENVER_REQUEST, "budget": 20})
    pools = await planner._retrieve_candidates(req)
    picks = planner._deterministic_fallback(req, pools)
    assert picks
    for p in picks:
        venue = pools[p["venue_id"]]
        assert (venue.cost_estimate_per_person or 0) <= 20
