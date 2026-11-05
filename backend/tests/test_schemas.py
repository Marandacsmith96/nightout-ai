"""Schema validation matrix — every object the AI or the user can produce is
checked at this boundary, so these tests are the contract's guardrails."""
import pytest
from pydantic import ValidationError

from app.schemas import Itinerary, PlanRequest, Venue

VALID = {
    "city": "Denver",
    "date": "2026-12-05",
    "group_size": 6,
    "budget": 60,
    "start_time": "18:00",
    "end_time": "23:30",
    "activities": ["Dinner"],
}


def test_valid_request_passes():
    PlanRequest(**VALID)


@pytest.mark.parametrize("field,value", [
    ("group_size", 0), ("group_size", 21), ("group_size", -3),
    ("budget", 4), ("budget", 1001),
    ("city", ""),
    ("start_time", "6pm"), ("end_time", "25:00"), ("end_time", "18:6"),
    ("date", "12/05/2026"),
])
def test_invalid_requests_rejected(field, value):
    payload = dict(VALID)
    payload[field] = value
    with pytest.raises(ValidationError):
        PlanRequest(**payload)


def test_after_midnight_end_time_allowed():
    # end <= start is legal: it means the night crosses midnight
    payload = dict(VALID, start_time="23:30", end_time="01:30")
    req = PlanRequest(**payload)
    assert req.end_time == "01:30"


def test_empty_activities_allowed_at_schema_level():
    # The schema stays permissive (form enforces UX rules); the planner handles
    # empty pools gracefully.
    PlanRequest(**{**VALID, "activities": []})


def test_venue_requires_coordinates_and_source():
    with pytest.raises(ValidationError):
        Venue(id="x", name="y")  # lat/lng required
    v = Venue(id="x", name="y", lat=1.0, lng=2.0)
    assert v.source == "demo"
    assert v.source_label == "Demo sample place"


def test_venue_price_label():
    v = Venue(id="x", name="y", lat=1.0, lng=2.0, price_level=3)
    assert v.price_label == "$$$"
    v2 = Venue(id="x2", name="y", lat=1.0, lng=2.0)
    assert v2.price_label == "price unknown"


def test_itinerary_round_trip():
    venue = Venue(id="den-01", name="Denver Biscuit Company", lat=39.74, lng=-104.95)
    it = Itinerary(
        id="abc12345", city="Denver", date="2026-12-05", stops=[], demo=True,
        budget={"per_person_total": 0, "budget": 60, "remaining": 60, "lines": [], "note": ""},
    )
    dumped = it.model_dump()
    restored = Itinerary(**dumped)
    assert restored.id == "abc12345"
    assert restored.demo is True
