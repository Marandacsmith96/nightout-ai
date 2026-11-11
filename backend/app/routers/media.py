"""Phase 7 multimodal endpoints: promo poster (FLUX) + voice-over (Chatterbox TTS).

`available: false` responses are NOT errors — they are the honest answer when
the feature isn't configured (the app's demo <-> live philosophy). Only real
upstream failures become HTTP errors.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas import Itinerary, PosterResponse, VoiceoverResponse
from app.services import media

router = APIRouter(prefix="/api/media", tags=["media"])


@router.post("/poster", response_model=PosterResponse)
async def create_poster(itinerary: Itinerary) -> PosterResponse:
    """Generate a promo poster for the itinerary (FLUX image model)."""
    try:
        result = await media.generate_poster(itinerary)
    except media.MediaUnavailable as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return PosterResponse(**result)


@router.post("/voiceover", response_model=VoiceoverResponse)
async def create_voiceover(itinerary: Itinerary) -> VoiceoverResponse:
    """Generate a spoken summary of the itinerary (Chatterbox TTS)."""
    try:
        result = await media.generate_voiceover(itinerary)
    except media.MediaUnavailable as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return VoiceoverResponse(**result)
