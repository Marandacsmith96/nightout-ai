# NightOut AI — Build Log

A plain-language record of how this app was built: phases, decisions, bugs, fixes,
and lessons. Updated as development progresses.

---

## Phase 1 — Project Setup and Design ✅ *(done)*

**Goal:** a beautiful, responsive homepage + the full planning form + the UI kit
the rest of the app will be built from.

### What was built
- Repository scaffold: `backend/` (FastAPI) + `frontend/` (React + Vite) + docs.
- Backend entry point with a `/api/health` endpoint and CORS configured for the
  Vite dev server. No real endpoints yet — those arrive in Phase 2.
- Homepage with the required hero: **"Less Planning. More Living."**, supporting
  copy, and a prominent **Plan My Night** button.
- The complete planning form: location, date, group size (1–20), budget
  (preset ranges + slider + custom amount), start/end time (nights can end after
  midnight), multi-select dietary restrictions (with manual "other"), 13 activity
  categories, 7 atmosphere choices, transportation, travel-distance preference,
  and a free-text "additional instructions" box.
- Reusable UI kit: buttons, toggle chips, slider, stepper, fields with inline
  validation errors, loading overlay, card, footer.
- Client-side validation with friendly inline messages (e.g. pick at least one
  activity; enter a city; end time after start).
- "Generate My Night Out" button currently exercises the loading indicator and
  then shows a summary of the request in the results area — the real AI
  generation lands in Phase 3.

### Design decisions
- **Dark nightlife theme:** deep navy/charcoal background with purple, pink, and
  warm amber accents; glass cards; soft glow; rounded corners. Chosen to match
  the brief and feel like a lifestyle/travel app, not a form.
- **Plain CSS with variables** instead of Tailwind — fewer moving parts, and the
  whole design lives in one place (`theme.css`). Tailwind can be added later if
  it earns its keep.
- **Same-page flow:** the planner and the results area share one page, so after
  generation the user scrolls straight into their night instead of navigating.
- **Validation on submit** (not on every keystroke) — friendlier for fast
  typing, still catches everything before the button does anything.

### Bugs found & fixed
- None found: `vite build` compiled clean (40 modules), backend `/api/health`
  responded, and the dev server served the app (HTTP 200). The only hiccup was
  curling the frontend one second before Vite finished booting — a readiness
  check, not a code bug.

### Lessons learned
- The multi-select chips and the budget slider are the two controls that need
  the most care on mobile; both are built touch-friendly from the start.
- Verify a dev server's readiness before curling it (Vite ~0.5 s boot on this
  machine, but the first curl fired too early).

---

## Phase 2 — Real Location Retrieval ✅ *(done)*

**Goal:** a real backend that retrieves and normalizes venues, with travel
times — and an honest demo mode until Google API keys exist.

### What was built
- **Data contract** (`schemas.py`): `PlanRequest`, `Venue`, `TravelEstimate`,
  `ItineraryStop`, `BudgetSummary`, `Itinerary` — everything the AI planner
  will emit gets validated against these before the frontend sees it.
- **Venue catalog service** with two explicit paths:
  - *Live:* Google Places Text Search + Place Details (addresses, coords,
    ratings, price level, opening hours, photo references) → normalized into
    the shared `Venue` schema with per-field `*_verified` flags.
  - *Demo (no key):* a sample catalog of real, well-known venues for Denver,
    Boulder, and Austin — every response carries `source: "demo"` and a
    `source_label`, and the UI shows a demo banner. Never disguised as live.
- **Budget & category filtering** at retrieval time (a $20/person cap never
  proposes a $45 place).
- **Travel-time service**: live Google Routes API when a key is set; otherwise
  a clearly-labeled estimate (great-circle × 1.25 for street paths, walking ≈
  1.35 m/s, driving ≈ 13 m/s, transit slower).
- **Endpoints**: `GET /api/venues/search` and `GET /api/travel/time`,
  both with honest source + note fields.
- **Tests**: 10 passing (`pytest`) — health, demo labeling, category filtering,
  budget caps, honest unknown-city handling, travel-time sanity.

### Design decisions
- **One schema for everything.** The AI (Phase 3) can only fill validated
  structures, so fabricated fields fail loudly instead of reaching the UI.
- **Demo data = real places, labeled as samples.** Nothing is invented; the
  labels ("Demo sample place") do the honesty work.
- **Fallback order matters:** live Routes first, estimate only when no key;
  estimate results are marked `source: "estimated"`.

### Bugs found & fixed
1. **Driving time was 234 minutes for a 3 km trip.** The formula multiplied
   seconds into minutes instead of dividing. Fixed to `distance / speed / 60`;
   a Denver downtown→LoHi drive now estimates ~4 min, walking ~38 min.
2. **Test asked the API for `limit=50` but the router caps at 20** (a
   deliberate live-mode cost guard) → 422. Tests now respect the documented cap.

### Lessons learned
- The first test suite paid for itself in one run: it caught the speed-unit
  bug and the API/test contract mismatch before the UI ever saw them.
- Keep the demo → live switch *in one place* (the catalog service) so behavior
  can't silently diverge.

---

*(Phase 3 — the AI itinerary generator — starts next.)*
