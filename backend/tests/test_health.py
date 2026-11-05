from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_ok():
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["app"] == "NightOut AI"
    # Always labeled: demo mode must be explicit, never silent.
    assert "demo_mode" in body


def test_unknown_route_404():
    assert client.get("/api/nope").status_code == 404
