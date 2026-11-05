"""Travel-time estimation tests (estimated mode — no Routes key in CI)."""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

DOWNTOWN_DENVER = (39.7392, -104.9903)
LOHI_DENVER = (39.7580, -105.0050)


def test_walking_estimate_is_sane():
    r = client.get(
        "/api/travel/time",
        params={"from_lat": DOWNTOWN_DENVER[0], "from_lng": DOWNTOWN_DENVER[1],
                "to_lat": LOHI_DENVER[0], "to_lng": LOHI_DENVER[1], "mode": "walking"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["source"] == "estimated"
    assert body["duration_min"] > 0
    assert body["distance_m"] > 0
    # ~2.7 km apart in a straight line; walking should be roughly 30-60 min.
    assert 20 <= body["duration_min"] <= 70


def test_driving_is_faster_than_walking():
    def dur(mode):
        r = client.get(
            "/api/travel/time",
            params={"from_lat": DOWNTOWN_DENVER[0], "from_lng": DOWNTOWN_DENVER[1],
                    "to_lat": LOHI_DENVER[0], "to_lng": LOHI_DENVER[1], "mode": mode},
        )
        return r.json()["duration_min"]

    assert dur("driving") < dur("walking")


def test_invalid_mode_rejected():
    r = client.get(
        "/api/travel/time",
        params={"from_lat": 1, "from_lng": 1, "to_lat": 2, "to_lng": 2, "mode": "teleport"},
    )
    assert r.status_code == 422
