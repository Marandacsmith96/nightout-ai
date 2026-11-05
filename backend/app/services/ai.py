"""AI itinerary service — the only place the language model is called.

Hard rules encoded here:
- The model ONLY picks venue ids from the candidate list we retrieved; it can
  never invent a business, address, hour, or price.
- Its output must parse as JSON with the documented shape; anything else is
  rejected and retried, then a deterministic fallback takes over.
- Numbers (schedule, costs, remaining budget) are computed by the app from
  venue data — never taken from the model's prose.
"""
from __future__ import annotations

import json
import re

from openai import AsyncOpenAI

from app.core.config import settings

_MODEL = "DeepSeek-V4-Flash-0731"

_SYSTEM = """You are the itinerary planner for NightOut AI. You plan a night out for a group.
You will receive the group's request and a list of CANDIDATE venues, each with a short id like 'den-01'.
RULES:
1. Choose venues ONLY from the candidate list, by id. Never invent a venue, address, price, or business hour.
2. Cover the activities the group asked for, in a realistic evening order (dinner first when included; drinks or dessert last when included).
3. Respect the per-person budget and the group's dietary needs as hard constraints: skip candidates that break them.
4. Reply with ONLY a JSON object, no prose, in this exact shape:
   {"stops": [{"kind": "dinner", "venue_id": "den-01", "reason": "One short natural sentence explaining why this fits the group."}]}
5. 'kind' must be one of: dinner, cocktail bars, casual drinks, live music, dancing, comedy shows, concerts, games & arcade bars, bowling, escape rooms, outdoor activities, dessert or coffee, something unexpected."""


def _client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=settings.openai_api_key or "missing-key",
        base_url=settings.openai_base_url or "https://api.openai.com/v1",
    )


def _strip_code_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return text


async def propose_itinerary(request: dict, candidates: list[dict]) -> tuple[dict | None, str]:
    """Ask the model to pick stops.

    Returns (proposal, error_hint): proposal is None when the AI is missing,
    unreachable, or keeps returning unparseable output; error_hint explains why
    so the caller can tell the user honestly.
    """
    if not settings.openai_api_key:
        return None, "no API key configured (OPENAI_API_KEY)"

    user_payload = {
        "group_request": {
            "city": request.get("city"),
            "date": request.get("date"),
            "group_size": request.get("group_size"),
            "budget_per_person": request.get("budget"),
            "start_time": request.get("start_time"),
            "end_time": request.get("end_time"),
            "activities": request.get("activities"),
            "restrictions": request.get("restrictions"),
            "atmosphere": request.get("atmosphere"),
            "transport": request.get("transport"),
            "distance_preference": request.get("distance"),
            "notes": request.get("notes"),
        },
        "candidate_venues": candidates,
    }

    messages = [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
    ]

    last_error = "AI request failed twice"
    for attempt in (1, 2, 3):
        try:
            resp = await _client().chat.completions.create(
                model=settings.openai_model or _MODEL,
                messages=messages,
                temperature=0,
                max_tokens=1600,
                extra_body={"enable_thinking": False},
            )
            raw = resp.choices[0].message.content or ""
            parsed = _parse_stops(raw)
            if parsed is not None:
                return parsed, ""
            last_error = f"AI response did not match the required JSON shape (attempt {attempt})"
        except Exception as exc:  # noqa: BLE001 — network/API errors fall through to fallback
            last_error = f"AI request failed: {type(exc).__name__}: {str(exc)[:120]}"
    return None, last_error


def _parse_stops(raw: str) -> dict | None:
    text = _strip_code_fences(raw)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if not m:
            return None
        try:
            data = json.loads(m.group(0))
        except json.JSONDecodeError:
            return None
    stops = data.get("stops") if isinstance(data, dict) else None
    if not isinstance(stops, list):
        return None
    cleaned = []
    for s in stops:
        if not isinstance(s, dict):
            return None
        kind = str(s.get("kind", "")).strip()
        vid = str(s.get("venue_id", "")).strip()
        reason = str(s.get("reason", "")).strip()
        if not kind or not vid:
            return None
        cleaned.append({"kind": kind, "venue_id": vid, "reason": reason})
    return {"stops": cleaned}
