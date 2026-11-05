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

## Phase 3 — AI Itinerary Generation ✅ *(done)*

**Goal:** turn the user's plan request into a real, validated, budget-checked
itinerary with actual venues — and render it beautifully.

### What was built
- **AI service** (`services/ai.py`): OpenAI-compatible chat call
  (`DeepSeek-V4-Flash-0731` via the course endpoint), temperature 0, thinking
  disabled, JSON-only prompt. The model may ONLY reference candidate venue ids
  we retrieved — it cannot invent places. Unparseable output is rejected and
  retried (3 attempts) with the failure reason surfaced honestly.
- **Planner orchestration** (`services/planner.py`):
  - Retrieves a candidate pool per selected activity (budget-filtered).
  - Asks the AI to pick stops; validates every pick against the candidate ids
    and requested kinds (unknown ids are rejected outright).
  - Computes the real schedule: start time, per-kind durations, travel between
    stops (walking/driving/transit), after-midnight end times.
  - Computes the budget summary from VENUE data — never from the model.
  - **Strict-budget guarantee**: if the total would exceed the per-person cap,
    trailing stops are trimmed with an honest note.
  - Deterministic fallback (top-rated picks) when the AI is missing or fails.
- **Endpoint**: `POST /api/plan/generate`.
- **Frontend**: itinerary timeline (numbered stop cards with times, venue,
  address, Maps link, cost with "est." flags, travel time, AI reason), budget
  box with per-stop lines + remaining/over, demo badges, edit notes, error
  panel, Regenerate button. Loading overlay wired to the real request.
- **Credentials**: backend `.env` (git-ignored) configured with the course
  endpoint + key — never committed, never printed.

### Verified
- 15 pytest tests green; live end-to-end call returned a 3-stop Denver night
  (vegetarian-friendly dinner → arcade bar → tap house), $46 of $60, walking
  times between stops, all venues from the real demo catalog.

### Bugs found & fixed
1. **AI proposal contract mismatch**: model returns `{"stops": [...]}` but the
   planner iterated it as a list → 500. Fixed the unpacking.
2. **Deterministic fallback could pick the same venue twice** (tag matching was
   stricter than retrieval's). Fallback now uses the SAME category→tag map as
   retrieval and never reuses a venue id.
3. **Strict budgets could be exceeded in total** (each stop ≤ cap, sum > cap).
   Added the trim-to-budget pass with an explanatory edit note.
4. **Transient AI endpoint failure** fell back silently; now retried 3× and the
   real reason is reported in the itinerary notes.

### Lessons learned
- Validation layers pay for themselves: the schema + id allowlist + budget
  trim guarantee the response is honest even when the model misbehaves.
- One test suite caught both a contracts bug and a budget invariant bug in the
  same run — keep the invariants in tests.
- Synthetic browser input (drive_preview) doesn't trigger React onChange —
  verify forms with real browser input or API-level tests instead.

---

## Phase 4 — Interactive AI Modifications ✅ *(done)*

**Goal:** let users change the plan conversationally — or stop by stop — without
losing what they didn't ask to change.

### What was built
- **Edit-intent AI** (`ai.interpret_edit`): interprets a natural-language
  instruction into ONE small structured op — `replace` / `add` / `remove` /
  `constraints` / `replan` — with a JSON contract and the same retry + honesty
  rules as generation.
- **Editor service** (`services/editor.py`) applies intents deterministically:
  - `replace`: fresh candidates retrieved for that stop's kind (honoring
    preferences like "cheaper", excluding current venues), AI picks, only that
    stop changes.
  - `add`: a new stop of the requested kind is inserted before drinks/dessert.
  - `remove`: only that stop is dropped.
  - `constraints`: **dietary changes re-pick venues; time/budget/transport
    changes re-schedule the SAME venues** — nothing the user didn't ask to
    change is thrown away.
  - `replan`: full rebuild **with locked stops forced back into place**.
- **Endpoints**: `POST /api/plan/edit`, `POST /api/plan/regenerate`.
- **Frontend**: AI chat panel beside the itinerary (suggested commands + free
  text + typing indicator + friendly replies), **Swap This Stop** and **Lock**
  buttons on every stop card; Regenerate respects locks.
- Schedule + budget always recomputed through the same planner helpers, so
  numbers never drift from the shown venues.

### Verified (live E2E, real AI)
- "Swap the drinks stop for dessert" → only the drinks stop changed.
- "We want to finish by 10 PM now" → dessert kept but dropped for schedule,
  night ends 21:32 ≤ 22:00.
- "Make dinner cheaper" → dinner $20 → $18, everything else untouched.
- 20 pytest tests green.

### Bugs found & fixed
1. **Constraint edits silently re-picked everything** (a replan threw away an
   earlier swap). Fixed: schedule-affecting constraints now preserve venues.
2. **Stops could end past the requested end time.** `compute_stops` now skips
   any stop that cannot COMPLETE before the end time, with an explanatory note.
3. Test-only fix: the "cheaper" filter test corrected to exclude the current
   venue (matching the app's real contract).

### Lessons learned
- Interpreting intent is where the model adds value; APPLYING it must be
  deterministic code with invariants — that split keeps the product honest.
- "Preserve what wasn't asked to change" is a rule you have to encode in the
  service, not something a prompt alone can guarantee.

---

## Phase 5 — Map, Save & Share ✅ *(done)*

**Goal:** see the night on a map, keep it, and hand it to the group chat.

### What was built
- **Mini-map ("your night at a glance")**: a dependency-free SVG view that
  plots every stop on its real latitude/longitude with numbered markers and a
  route line — works in demo mode, no API key — plus a **"View full map"**
  link that opens Google Maps with ALL stops pre-loaded as a directions route.
- **Save My Night**: itineraries persist in `localStorage` with a load/delete
  list in the side panel (up to 20 saved).
- **Share**:
  - **Copy for group chat** — a clean, formatted text itinerary
    (times, addresses, costs, Maps links) ready to paste into any messaging app.
  - **Share link** — the whole plan is packed into the URL fragment; opening
    the link restores the itinerary (and its edit chat still works).
- **Surprise Me** — generates a complete random-but-sensible plan (city, next
  Saturday, group size, budget, activities, "Surprise me" atmosphere) with one
  click, no other input required.
- Small UX: header action row on the itinerary, flash confirmation toasts.

### Verified
- Frontend builds clean; share round-trip (encode → decode → same itinerary)
  verified; backend health + frontend serving confirmed.

### Design decisions
- Map without a key: the embedded mini-map + Google Maps route link beat a
  keyless iframe that can only show one marker.

---

## Phase 6 — Tests, Docs & Polish ✅ *(done)*

**Goal:** make it presentation-ready: a real test story, real docs, and a
script you can present from.

### What was built
- **49 automated tests** (backends, offline, ~27 s):
  - schema validation matrix (group size/budget bounds, **time & date format
    patterns**, after-midnight end times, venue/price-label rules)
  - AI parser robustness (fenced JSON, prose-wrapped JSON, garbage → None)
  - consistency invariants on every generated itinerary: **no duplicate
    venues, chronological non-overlapping times, budget lines sum to total,
    total never exceeds the cap, demo labeling always present, unrequested
    kinds never appear, time-window overflows reported not crashed**
  - endpoint tests (health, venues, travel, planner, editor)
- **README rewritten**: features table, architecture + three-layer honesty
  design, quickstart, config/key guide, API reference, project layout, scope.
- **docs/DEMO_SCRIPT.md**: a 4-minute live-demo walkthrough with backup
  answers for the presentation.
- **Polish**: favicon (🌙), theme-color meta.

### Bugs found & fixed
1. **Dates and times were unvalidated at the API boundary** (a request with
   `start_time: "6pm"` sailed through). The new schema matrix caught it;
   `date`/`start_time`/`end_time` now have strict patterns.
2. The invariant suite initially ran 4 minutes (live AI per call); stubbing
   the AI to the deterministic path cut it to ~27 s without weakening the
   invariants (they test the app's consistency, not the model's taste).

### Verified
- 49/49 tests green, frontend builds clean, both servers live-verified,
  repo pushed to **github.com/Marandacsmith96/nightout-ai** (public `main`).

### Final state of the project
A complete, working application: honest place retrieval (live-ready, labeled
demo fallback), validated AI itinerary generation, conversational edits that
preserve what you didn't ask to change, budget guarantees, maps, save/share,
49 tests, a README that documents the whole thing, and a demo script ready
for an MBA presentation. Git history tells the whole story in 8 commits.

---

## Hotfix — "Generate My Night Out" returned nothing (first real-user bug) ✅

**Symptom:** clicking *Generate My Night Out* in the browser failed silently —
the quickly-hidden error panel said "Field required".

**Root cause (found via the backend log + payload reproduction):** the form
sent `groupSize` / `startTime` / `endTime`, but the API contract (Pydantic)
defines `group_size` / `start_time` / `end_time`. Every automated test and
E2E script used snake_case, so the mismatch existed since Phase 3 and only a
real browser click exposed it. The user WAS the first true integration test.

**Fix:** one adapter module (`frontend/src/lib/apiPlan.js`, `toApiPlan`) is now
the single place that maps form (camelCase) → API (snake_case). Form submit,
Surprise Me, and the edit chat all route through it, so the two sides can't
drift again. The API client also now reports validation errors with a readable
message instead of a raw JSON blob.

**Verified:** adapter unit-checked, mapped payload → HTTP 200 with a real
itinerary, frontend builds. Also added a readable-error fallback so any future
validation problem shows a plain sentence instead of a dead button.

**Lesson learned:** contract tests must exercise the *actual* client payload
shape, not just the backend's own view of it — add a fixture that replays the
frontend's real request body.

---
