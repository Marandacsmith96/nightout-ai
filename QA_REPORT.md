# NightOut AI — QA Pass Report (2026-11-09)

Independent QA pass by Sam, running the app locally on macOS (Python 3.11, Node 26).
Configuration tested: **real AI (DeepSeek-V4-Flash-0731 via course endpoint) + labeled demo-mode places**
(the same experience a keyless professor would get).

## Summary

The app is in very good shape. The backend is excellent — 49/49 tests pass, and every
conversational-edit and budget scenario I threw at it behaved correctly. Two real bugs
found (one frontend date bug, one docs/compatibility gap). Everything else that looked
like a bug at first turned out to be my test harness lying to me (details below so we
don't re-investigate them).

## Bugs found

### 1. Itinerary header shows the wrong day (off-by-one date bug) — frontend
**Reproduced live.** A plan for **Saturday, Nov 14, 2026** displays
**"Friday, November 13"** in the itinerary header.

Cause: `new Date("2026-11-14")` in JS parses as UTC midnight; `toLocaleDateString`
renders it in the local timezone, which shifts it back one day in every US timezone.
Affects **3 places**:
- `frontend/src/components/ItineraryView.jsx:45` (itinerary header)
- `frontend/src/lib/share.js:38` (saved-night label — confirmed "Denver · 11/13/2026")
- `frontend/src/lib/share.js:71` (Copy-for-group-chat text)

Fix: parse the date as local (e.g. `new Date(date + "T00:00:00")` or split the string)
in one helper and use it in all three places.

### 2. Backend silently requires Python 3.10+, nothing documents it — docs/repro gap
On a fresh Mac with the default system Python (3.9.6), the backend **fails to boot and
fails to collect tests** (`TypeError: Unable to evaluate type annotation 'float | None'`
in pydantic). The code uses PEP 604 unions (`X | None`) in pydantic models, which need
Python 3.10+ (or the `eval_type_backport` package on 3.9).

The professor's "runnable code, easily test myself" deliverable is at risk if he or
any teammate uses a default Python. README/quickstart never state a minimum version.

Fix options (pick one or both):
- Add `eval_type_backport` to `backend/requirements.txt` (pydantic auto-uses it on 3.9) — keeps 3.9 working.
- Or document **"Python 3.10+ required"** prominently in README + CONTRIBUTING.

## Verified working (E2E, live)

| Area | Result |
|---|---|
| Backend tests | 49/49 pass on Python 3.11 (0.46 s with stubbed AI) |
| Frontend build | `npm run build` clean (48 modules) |
| Form → generate → itinerary | Real AI, 2–3 stops, times, travel, per-person costs, AI reasons |
| Budget guard | $34 of $60; tiny-budget edge trimmed to exactly $12 with explanatory note |
| Honest data labeling | "🧪 sample places" badge everywhere in demo mode |
| Chat edit: "Make dinner cheaper" | Dinner-only change ($20 → cheaper), other stops untouched |
| Chat edit: "finish by 10 PM" | Venue kept, later stop dropped with explanatory note |
| Chat edit: swap-refusal | Politely refused when target stop no longer existed (no crash) |
| After-midnight end times | `end_time 00:30` accepted and scheduled correctly |
| Bad input | 422 with readable message surfaced in the UI error panel |
| Surprise Me | One click → random-but-sensible plan (Austin, $25/$100) |
| Lock + Regenerate | Locked stop survives full regeneration |
| Save | localStorage, saved list, load/delete |
| Share link | Full round trip: encode → reload → itinerary restored (chat intact) |
| Swap this stop | (Code path = edit intent; not separately browser-tested) |

## Investigated — NOT bugs (false alarms, don't re-open)

- **"Chat edit does nothing"** — my synthetic typing didn't trigger React's onChange
  (test artifact). Real input/chips work; Send is correctly disabled on empty drafts.
- **"Surprise Me does nothing"** — my selector was matching the *"Surprise me"*
  atmosphere chip, not the button (both contain "Surprise me"). Real button works.
- **"Share link seems dead"** — by design it copies the URL to the clipboard (flash
  confirms); round trip manually verified.
- **Date-picker garbage value ("61114-02-02")** — artifact of typing into an HTML date
  input; real users use the native picker.

## Minor observations (nice-to-haves)

1. Share-link flash says *"anyone with this browser can open it"* — under-sells it;
   suggest *"anyone with this link"* (PlannerPage.jsx:106).
2. `docs/DEMO_SCRIPT.md` setup block uses a Windows path (`.venv/Scripts/python.exe`);
   add the Mac/Linux equivalent.
3. `pytest-asyncio` deprecation warning about `asyncio_default_fixture_loop_scope`
   (cosmetic; silence it in `pyproject.toml`/config if desired).
4. No branches/PRs yet in git history; CONTRIBUTING.md already says never push to main
   directly — start using branch → PR now that there are two contributors.
5. `$12`-budget edge case tripped the AI 3× (invalid JSON) → honest fallback note shown.
   By-design behavior; worth knowing for the demo's backup answers.

## Not yet tested

- Swap-This-Stop button (UI), lock button (UI) — logic covered by API tests; click
  through on a real browser recommended.
- Mobile/narrow viewport rendering.
- Live Google Places/Routes mode (no API key available locally).
- The "Dinner" activity chip once failed to appear in the live summary during my first
  form fill (couldn't reproduce; probably input timing). Worth one manual click-test.

## Environment notes

- Local clone: `Final Project/nightout-ai` (backend `.env` created locally from the
  course endpoint config — git-ignored, not committed).
- Test stack: backend on Python 3.11.16 (`~/.local/bin/python3.11`), frontend Node 26.
- The headless-browser harness I used is unreliable in this environment (tabs die to
  about:blank, synthetic clicks sometimes not delivered) — several "bugs" above were
  harness artifacts, which is why they were re-verified via code reading + API-level E2E.
  Any manual user test by a human is worth more than all of the above for final QA.
