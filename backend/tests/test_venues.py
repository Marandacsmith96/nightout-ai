"""Demo-mode venue retrieval tests (no API keys in CI)."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_search_denver_dinner_returns_labeled_demo_venues():
    r = client.get("/api/venues/search", params={"query": "dinner", "city": "Denver", "limit": 20})
    assert r.status_code == 200
    body = r.json()
    assert body["source"] == "demo"
    assert "demo" in body["source_label"].lower()
    assert len(body["venues"]) > 0
    for v in body["venues"][:3]:
        assert v["source"] == "demo"
        assert v["name"]
        assert v["lat"] and v["lng"]
        assert v["google_maps_url"].startswith("https://www.google.com/maps/")


def test_search_category_filtering():
    r = client.get("/api/venues/search", params={"query": "cocktail bars", "city": "Denver", "limit": 20})
    venues = r.json()["venues"]
    assert venues, "expected cocktail venues in Denver demo data"
    assert all("cocktail" in v["tags"] for v in venues)


def test_search_budget_filter_respected():
    r = client.get("/api/venues/search", params={"query": "dinner", "city": "Denver", "budget": 20, "limit": 20})
    venues = r.json()["venues"]
    assert venues, "expected dinner venues under $20 in Denver demo data"
    assert all(
        (v["cost_estimate_per_person"] or 0) <= 20 for v in venues
    ), "budget filter must never propose venues over the per-person cap"


def test_unknown_city_gets_honest_empty_response():
    r = client.get("/api/venues/search", params={"query": "dinner", "city": "Nowhereville"})
    body = r.json()
    assert body["venues"] == []
    assert "sample venues" in body["note"]  # explains why, instead of inventing data


def test_plan_schema_validates_group_size():
    bad = {"city": "Denver", "date": "2026-12-05", "group_size": 99, "budget": 60,
           "start_time": "19:00", "end_time": "23:30"}
    r = client.post("/api/plan/validate", json=bad)
    # Endpoint does not exist yet in Phase 2 — the schema itself is what we assert on.
    from pydantic import ValidationError
    from app.schemas import PlanRequest
    try:
        PlanRequest(**bad)
        raised = False
    except ValidationError:
        raised = True
    assert raised
    assert r.status_code == 404  # planned Phase 3 endpoint, not present yet
