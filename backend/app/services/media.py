"""Multimodal media service (Phase 7): promo poster (FLUX) + voice-over (Chatterbox TTS).

Follows the same honesty rules as the rest of the app:
- features are only offered when configured (like the demo <-> live split);
- every response says exactly which model produced it and shows the prompt /
  spoken text that was sent, so nothing is hidden;
- upstream failures surface as friendly, actionable notes — never a silent 500.
"""
from __future__ import annotations

import base64
import httpx

from app.core.config import settings

_TIMEOUT = 120.0
_MAX_IMAGE_BYTES = 8 * 1024 * 1024
_NARRATION_LIMIT = 500


class MediaUnavailable(Exception):
    """Safe, user-facing failure of a media service (op drawing to HTTP 502)."""


def _auth_headers(key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {key}"}


def _pretty_time(hhmm: str) -> str:
    try:
        h, m = map(int, hhmm.split(":"))
        suffix = "AM" if h < 12 else "PM"
        h12 = h % 12 or 12
        return f"{h12}:{m:02d} {suffix}" if m else f"{h12} {suffix}"
    except ValueError:
        return hhmm


def poster_prompt(itinerary) -> str:
    """Build the FLUX prompt from a *validated* itinerary.

    Art direction is deliberately **abstract**: FLUX.2-klein reflexively paints
    pseudo-signage/lettering into scene compositions (verified live in QA), so
    the poster asks for pure light-and-color art with no objects, no scene,
    and no signage. The app owns ALL typography — the modal overlays the crisp
    city/date caption on top, so words are never left to an image model.
    """
    city = itinerary.city
    kinds = ", ".join(dict.fromkeys(s.kind for s in itinerary.stops[:8])) or "a fun evening"
    return (
        f"Abstract nightlife poster artwork for a night out in {city}, inspired "
        f"by an evening of {kinds}. "
        "Deep navy background with flowing neon gradient waves in purple, pink "
        "and warm gold, a subtle crescent moon, floating glowing bokeh "
        "particles like city lights. Elegant, premium, calm composition. "
        "No objects, no people, no buildings, no scene, no silhouettes. "
        "No text, no lettering, no words, no numbers, no signs — pure "
        "abstract art only."
    )


def narration_text(itinerary) -> str:
    """A short spoken summary built from itinerary facts (never model prose)."""
    lines = [f"Here is your {itinerary.city} night out!"]
    for s in itinerary.stops[:8]:
        cost = (
            f"about {s.cost_per_person} dollars per person"
            if s.cost_per_person is not None
            else "no cost estimate"
        )
        lines.append(f"At {_pretty_time(s.start)}, {s.title}, a {s.kind} stop, {cost}.")
    if itinerary.budget:
        lines.append(
            f"The total is {itinerary.budget.per_person_total} dollars per person, "
            f"with about {itinerary.budget.remaining} dollars to spare."
        )
    return " ".join(lines)[:_NARRATION_LIMIT]


async def generate_poster(itinerary) -> dict:
    """Generate a promo poster; returns a PosterResponse-shaped dict."""
    if not settings.flux_configured:
        return {
            "available": False,
            "source": "not configured",
            "note": "Poster studio isn't configured — add FLUX_BASE_URL and "
            "FLUX_API_KEY to backend/.env to enable it.",
        }

    prompt = poster_prompt(itinerary)
    payload = {
        "model": settings.flux_model,
        "prompt": prompt,
        "n": 1,
        "size": "768x768",
        "response_format": "b64_json",
        "output_format": "png",
        "num_inference_steps": 8,
    }

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await client.post(
                f"{settings.flux_base_url}/images/generations",
                headers=_auth_headers(settings.flux_api_key),
                json=payload,
            )
        r.raise_for_status()
        data = r.json()
        raw = base64.b64decode(data["data"][0]["b64_json"], validate=True)
        if len(raw) > _MAX_IMAGE_BYTES:
            raise MediaUnavailable("Poster service returned an oversized image. Please retry.")
    except httpx.HTTPError as exc:
        raise MediaUnavailable(
            f"The poster service couldn't be reached ({type(exc).__name__}). "
            "Wait a moment and try again."
        ) from exc
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise MediaUnavailable("The poster service returned an unreadable image. Please retry.") from exc

    return {
        "available": True,
        "media_type": "image/png",
        "data_b64": base64.b64encode(raw).decode("ascii"),
        "source": "flux",
        "source_label": "AI-generated with FLUX",
        "prompt": prompt,
        "note": "",
    }


def _audio_media_type(audio: bytes) -> str:
    """Sniff the actual container and label it honestly.

    We *ask* for MP3, but the class TTS occasionally responds with an M4A
    (ftyp) stream instead. The browser refuses to play bytes labeled with the
    wrong MIME type, so the label must match what we actually received.
    """
    if audio[:3] == b"ID3" or audio[:2] == b"\xff\xfb":
        return "audio/mpeg"
    if audio[4:8] == b"ftyp":
        return "audio/mp4"
    if audio[:4] == b"RIFF" and audio[8:12] == b"WAVE":
        return "audio/wav"
    return "audio/mpeg"  # safest default


async def generate_voiceover(itinerary) -> dict:
    """Generate a spoken summary; returns a VoiceoverResponse-shaped dict."""
    if not settings.tts_configured:
        return {
            "available": False,
            "source": "not configured",
            "note": "Voice-over isn't configured — add TTS_BASE_URL and "
            "TTS_API_KEY to backend/.env to enable it.",
        }

    narration = narration_text(itinerary)
    payload = {
        "model": settings.tts_model,
        "input": narration,
        "voice": "default",
        "language_id": "en",
        "response_format": "mp3",
    }

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await client.post(
                f"{settings.tts_base_url}/v1/audio/speech",
                headers=_auth_headers(settings.tts_api_key),
                json=payload,
            )
        r.raise_for_status()
        audio = r.content
        if not audio:
            raise MediaUnavailable("The voice-over service returned empty audio. Please retry.")
    except httpx.HTTPError as exc:
        raise MediaUnavailable(
            f"The voice-over service couldn't be reached ({type(exc).__name__}). "
            "Wait a moment and try again."
        ) from exc

    return {
        "available": True,
        "media_type": _audio_media_type(audio),
        "data_b64": base64.b64encode(audio).decode("ascii"),
        "source": "chatterbox",
        "source_label": "AI voice-over with Chatterbox",
        "narration": narration,
        "note": "",
    }
