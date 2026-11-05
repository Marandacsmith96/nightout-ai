"""Consistency invariants — whatever the AI does, the generated itinerary must
never violate these. These tests run against the demo path (no live keys)."""
import asyncio

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import PlanRequest
from app.services import ai, planner

client = TestClient(app)

REQ = {
    "city": "Denver", "date": "2026-12-05", "group_size": 6, "budget": 60,
    "start_time": "18:00", "end_time": "23:30",
    "activities": ["Dinner", "Games & arcade bars", "Casual drinks"],
    "atmosphere": "Casual & relaxed", "transport": "Walking",
    "distance": "Moderate travel between stops is okay", "notes": "",
}


@pytest.fixture(autouse=True)
def offline_ai(monkeypatch):
    """Deterministic fallback path: invariants are about consistency, not the
    model's taste — and the suite stays fast without network calls."""

    async def fake_propose(request, candidates):
        return None, "stubbed for tests"

    monkeypatch.setattr(ai, "propose_itinerary", fake_propose)


def _generate(payload=None):
    r = client.post("/api/plan/generate", json=payload or REQ)
    assert r.status_code == 200
    return r.json()


def test_no_duplicate_venues():
    it = _generate()
    ids = [s["venue"]["id"] for s in it["stops"]]
    assert len(ids) == len(set(ids)), f"duplicate venues: {ids}"


def test_times_are_chronological():
    it = _generate()
    prev_end = None
    for s in it["stops"]:
        if prev_end is not None:
            assert s["start"] >= prev_end, f"{s['title']} overlaps: start {s['start']} < prev end {prev_end}"
        assert s["start"] < s["end"]
        prev_end = s["end"]


def test_budget_lines_sum_to_total():
    it = _generate()
    b = it["budget"]
    assert sum(line["amount"] for line in b["lines"]) == b["per_person_total"]


def test_budget_never_exceeds_cap():
    for budget in (15, 25, 40, 80):
        it = _generate({**REQ, "budget": budget})
        assert it["budget"]["per_person_total"] <= budget, (
            f"budget {budget}: total {it['budget']['per_person_total']}"
        )


def test_every_stop_carries_complete_venue():
    it = _generate()
    for s in it["stops"]:
        v = s["venue"]
        assert v["name"] and v["address"]
        assert v["lat"] is not None and v["lng"] is not None
        assert v["google_maps_url"].startswith("https://www.google.com/maps/")


def test_demo_labeling_when_demo():
    it = _generate()
    assert it["demo"] is True
    assert "sample" in it["demo_note"].lower()
    for s in it["stops"]:
        assert s["venue"]["source"] == "demo"


def test_unrequested_kinds_never_appear():
    it = _generate()
    requested = {a.lower() for a in REQ["activities"]}
    for s in it["stops"]:
        assert s["kind"] in requested, f"unrequested kind {s['kind']} in plan"


def test_timeouts_reported_not_crashed():
    # a very short window: stops that can't fit are skipped with a note
    it = _generate({**REQ, "start_time": "23:00", "end_time": "23:30"})
    assert it["stops"] == [] or any("skipped" in n for n in it["edits"])


# ---- parser robustness: garbage in, None out (never a crash) ----

def test_parse_stops_accepts_clean_json():
    raw = '{"stops": [{"kind": "dinner", "venue_id": "den-01", "reason": "nice"}]}'
    assert ai._parse_stops(raw)["stops"][0]["venue_id"] == "den-01"


def test_parse_stops_accepts_fenced_json():
    raw = '```json\n{"stops": [{"kind": "dinner", "venue_id": "den-01", "reason": "nice"}]}\n```'
    assert ai._parse_stops(raw) is not None


def test_parse_stops_accepts_prose_wrapped_json():
    raw = 'Sure! Here you go: {"stops": [{"kind": "dinner", "venue_id": "den-01", "reason": "y"}]} Hope that helps!'
    assert ai._parse_stops(raw) is not None


def test_parse_stops_rejects_garbage():
    assert ai._parse_stops("not json at all") is None
    assert ai._parse_stops("") is None
    assert ai._parse_stops('{"stops": "nope"}') is None
    assert ai._parse_stops('{"stops": [{"kind": "dinner"}]}') is None  # missing venue_id
    assert ai._parse_stops('{"stops": [123]}') is None


def test_parse_intent_matrix():
    assert ai._parse_intent('{"op": "replace", "index": 1}')["op"] == "replace"
    assert ai._parse_intent('{"op": "constraints", "constraints": {"budget": 40}}')["constraints"]["budget"] == 40
    assert ai._parse_intent('{"op": "teleport"}') is None
    assert ai._parse_intent("garbage") is None
    assert ai._parse_intent('{"op": "none", "reply": "ok"}')["op"] == "none"
