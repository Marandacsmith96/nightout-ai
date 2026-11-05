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

*(Phase 2 — real location retrieval — starts next.)*
