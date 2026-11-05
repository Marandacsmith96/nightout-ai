"""Itinerary endpoints: generation (Phase 3) + conversational edits (Phase 4)."""
from __future__ import annotations

from fastapi import APIRouter

from app.schemas import EditRequest, EditResponse, Itinerary, PlanRequest, RegenerateRequest
from app.services import editor, planner

router = APIRouter(prefix="/api/plan", tags=["plan"])


@router.post("/generate", response_model=Itinerary)
async def generate_itinerary(request: PlanRequest) -> Itinerary:
    return await planner.generate(request)


@router.post("/edit", response_model=EditResponse)
async def edit_itinerary(payload: EditRequest) -> EditResponse:
    result = await editor.edit_itinerary(
        payload.request, payload.itinerary, payload.instruction, payload.locked_indices
    )
    return EditResponse(**result)


@router.post("/regenerate", response_model=EditResponse)
async def regenerate_itinerary(payload: RegenerateRequest) -> EditResponse:
    # No previous itinerary reference for locks when regenerating from scratch;
    # the frontend passes locked indices only meaningful with an itinerary, so
    # locks are handled via /edit (op=replan) instead.
    fresh = await planner.generate(payload.request)
    return EditResponse(itinerary=fresh, reply="Rebuilt your night from scratch.")
