"""NightOut AI — API contract (Phase 2).

Every object the frontend and the AI planner exchange is defined here so the
whole pipeline validates against one schema and nothing fabricated slips
through unchecked.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class PlanRequest(BaseModel):
    """What the user tells us about their night (submitted by the form)."""
    city: str = Field(min_length=1, max_length=80)
    state: str = ""
    date: str  # YYYY-MM-DD
    group_size: int = Field(ge=1, le=20)
    budget: int = Field(ge=5, le=1000)  # $ per person
    start_time: str  # HH:MM (24h)
    end_time: str  # HH:MM (24h); may be <= start_time to mean "ends after midnight"
    restrictions: list[str] = []
    activities: list[str] = []
    atmosphere: str = "Casual & relaxed"
    transport: str = "Walking"
    distance: str = "Moderate travel between stops is okay"
    notes: str = ""


class Venue(BaseModel):
    """A normalized place from Google Places (live) or the sample catalog (demo).

    `source` is always explicit so the UI can badge demo data and the planner
    never treats sample entries as verified facts.
    """
    id: str
    name: str
    address: str = ""
    lat: float
    lng: float
    rating: float | None = None
    rating_verified: bool = False
    price_level: int | None = None  # 0 unknown .. 4 $$$$
    price_verified: bool = False
    cost_estimate_per_person: int | None = None  # derived, clearly an estimate
    hours: list[str] | None = None
    hours_verified: bool = False
    tags: list[str] = []
    photo_reference: str | None = None
    photo_url: str | None = None
    google_maps_url: str = ""
    source: str = "demo"  # "google_places" | "demo"
    source_label: str = "Demo sample place"

    @property
    def price_label(self) -> str:
        if self.price_level is None or self.price_level <= 0:
            return "price unknown"
        return "$" * self.price_level


class VenueSearchResponse(BaseModel):
    query: str
    city: str
    source: str
    source_label: str
    note: str = ""
    venues: list[Venue] = []


class TravelEstimate(BaseModel):
    mode: str  # walking | driving | transit
    distance_m: int
    duration_min: int
    source: str  # "google_routes" | "estimated"
    source_label: str


class ItineraryStop(BaseModel):
    """One stop in a generated night (Phase 3 fills these; schema defined now)."""
    index: int
    kind: str  # dinner | activity | drinks | dessert | coffee | walk ...
    title: str
    start: str
    end: str
    venue: Venue | None = None
    note: str = ""  # why it fits the group
    travel_from_previous_min: int | None = None
    travel_from_previous_mode: str | None = None
    travel_from_previous_source: str | None = None
    cost_per_person: int | None = None
    cost_verified: bool = False


class BudgetSummary(BaseModel):
    per_person_total: int
    budget: int
    remaining: int
    lines: list[dict] = Field(default_factory=list)  # [{label, amount, verified}]
    note: str = "Estimates may exclude taxes, tips, and fees."


class Itinerary(BaseModel):
    id: str
    city: str
    date: str
    stops: list[ItineraryStop]
    budget: BudgetSummary
    generated_at: str = ""
    demo: bool = False
    demo_note: str = ""
    edits: list[str] = []


class EditRequest(BaseModel):
    """A conversational change to an existing itinerary."""
    instruction: str = Field(min_length=1, max_length=500)
    request: PlanRequest  # current plan request (may have been edited before)
    itinerary: Itinerary  # the itinerary as currently displayed
    locked_indices: list[int] = []


class EditResponse(BaseModel):
    itinerary: Itinerary
    reply: str


class RegenerateRequest(BaseModel):
    request: PlanRequest
    locked_indices: list[int] = []
