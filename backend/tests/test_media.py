"""Phase 7 media endpoints — offline by design.

Upstream services are either stubbed (monkeypatched service layer) or
unconfigured, so the suite never touches the network. The pure builders
(prompt / narration) get real unit coverage because what they emit is what
the external models actually receive.
"""
import base64

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import BudgetSummary, Itinerary, ItineraryStop, Venue
from app.services import media

client = TestClient(app)


def _itinerary() -> dict:
    venue = Venue(
        id="den-01",
        name="Test Table",
        address="1 Test St",
        lat=39.75,
        lng=-104.99,
        price_level=2,
        cost_estimate_per_person=20,
    )
    stop = ItineraryStop(
        index=1,
        kind="dinner",
        title="Test Table",
        start="19:00",
        end="20:30",
        venue=venue,
        cost_per_person=20,
        note="fits the group",
    )
    it = Itinerary(
        id="p7",
        city="Denver",
        date="2026-11-14",
        stops=[stop],
        budget=BudgetSummary(per_person_total=20, budget=60, remaining=40),
    )
    return it.model_dump()


def test_health_reports_media_configuration():
    body = client.get("/api/health").json()
    assert "media_configured" in body
    assert set(body["media_configured"]) == {"poster", "voiceover"}


def test_poster_prompt_builder_uses_only_verified_facts():
    it = Itinerary.model_validate(_itinerary())
    prompt = media.poster_prompt(it)
    assert "Denver" in prompt
    assert "inspired by an evening of dinner" in prompt
    # typography stays out of the image — the app's UI owns all words
    assert "no text, no lettering" in prompt.lower()


def test_narration_builder_reads_like_a_human_hour():
    it = Itinerary.model_validate(_itinerary())
    text = media.narration_text(it)
    assert "Denver" in text
    assert "7 PM" in text
    assert "Test Table" in text
    assert "20 dollars" in text


@pytest.mark.parametrize("endpoint", ["/api/media/poster", "/api/media/voiceover"])
def test_unconfigured_features_are_honest_not_erroring(monkeypatch, endpoint):
    for var in ("FLUX_API_KEY", "FLUX_BASE_URL", "TTS_API_KEY", "TTS_BASE_URL"):
        monkeypatch.delenv(var, raising=False)
    r = client.post(endpoint, json=_itinerary())
    assert r.status_code == 200
    body = r.json()
    assert body["available"] is False
    assert body["source"] == "not configured"
    assert body["note"]


def test_poster_configured_returns_image(monkeypatch):
    monkeypatch.setenv("FLUX_API_KEY", "test-key")
    monkeypatch.setenv("FLUX_BASE_URL", "http://flux.test/v1")

    async def fake_poster(itinerary):
        return {
            "available": True,
            "media_type": "image/png",
            "data_b64": base64.b64encode(b"fake-png-bytes").decode("ascii"),
            "source": "flux",
            "source_label": "AI-generated with FLUX",
            "prompt": "a poster prompt",
            "note": "",
        }

    monkeypatch.setattr(media, "generate_poster", fake_poster)
    r = client.post("/api/media/poster", json=_itinerary())
    assert r.status_code == 200
    body = r.json()
    assert body["available"] is True
    assert body["media_type"] == "image/png"
    assert base64.b64decode(body["data_b64"]) == b"fake-png-bytes"
    assert body["source"] == "flux"


@pytest.mark.parametrize(
    "blob, expected",
    [
        (b"ID3\x04\x00\x00\x00\x00\x00\x00", "audio/mpeg"),
        (b"\xff\xfb\x90\x64", "audio/mpeg"),
        (b"\x00\x00\x00\x18ftypM4A \x00\x00\x00\x00", "audio/mp4"),
        (b"RIFF\x24\x00\x00\x00WAVEfmt ", "audio/wav"),
        (b"\x00\x01\x02\x03\x04\x05\x06\x07", "audio/mpeg"),
    ],
)
def test_audio_media_type_sniffs_container(blob, expected):
    assert media._audio_media_type(blob) == expected


def test_voiceover_configured_returns_audio(monkeypatch):
    monkeypatch.setenv("TTS_API_KEY", "test-key")
    monkeypatch.setenv("TTS_BASE_URL", "http://tts.test")

    async def fake_voiceover(itinerary):
        return {
            "available": True,
            "media_type": "audio/mpeg",
            "data_b64": base64.b64encode(b"fake-mp3-bytes").decode("ascii"),
            "source": "chatterbox",
            "source_label": "AI voice-over with Chatterbox",
            "narration": "Here is your Denver night out!",
            "note": "",
        }

    monkeypatch.setattr(media, "generate_voiceover", fake_voiceover)
    r = client.post("/api/media/voiceover", json=_itinerary())
    assert r.status_code == 200
    body = r.json()
    assert body["available"] is True
    assert body["media_type"] == "audio/mpeg"
    assert base64.b64decode(body["data_b64"]) == b"fake-mp3-bytes"
    assert body["source"] == "chatterbox"


def test_upstream_failure_is_a_clean_502(monkeypatch):
    monkeypatch.setenv("FLUX_API_KEY", "test-key")
    monkeypatch.setenv("FLUX_BASE_URL", "http://flux.test/v1")

    async def broken_poster(itinerary):
        raise media.MediaUnavailable("The poster service couldn't be reached (ConnectError).")

    monkeypatch.setattr(media, "generate_poster", broken_poster)
    r = client.post("/api/media/poster", json=_itinerary())
    assert r.status_code == 502
    assert "couldn't be reached" in r.json()["detail"]
