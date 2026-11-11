# NightOut AI — Final Presentation Outline

**MBAX 6418 · Group I · November 2026** — 10–12 minutes + Q&A.
Companion to `NightOut_AI_Final_Presentation.pptx` (12 slides, speaker notes
in the deck). Slide speaker notes contain suggested narration; the live-demo
walkthrough lives in `docs/DEMO_SCRIPT.md`.

**⚠️ To fill in before presenting (do NOT leave blank):**
- Slide 7 (Build stack): each member's actual AI coding tools + models.
  Known so far: Hermes Agent with DeepSeek-V4-Flash-0731 (Katie's sessions).
- Slide 11 (Contributions): confirm everyone's roles + who presents.

## Slide map

| # | Slide | Rallying line |
|---|---|---|
| 1 | Title | Less Planning. More Living. — Group I, all members, date |
| 2 | The problem | Group plans are a group project |
| 3 | Our answer | One form in → a full, real-venue night out, editable by chat |
| 4 | Core features | Form, AI itinerary, budget guard, chat edits, locks, map, save/share, Surprise Me |
| 5 | Demonstration | Real app screenshots (home + generated itinerary) |
| 6 | Multimodal | FLUX promo poster + Chatterbox voice-over, honestly labeled |
| 7 | Build stack | Hermes Agent + DeepSeek-V4-Flash-0731; branches/PRs; CI; click-through QA |
| 8 | App stack | React+Vite / FastAPI+Pydantic / DeepSeek / FLUX / Chatterbox / Google (optional) / localStorage |
| 9 | Sources | Built from scratch; labeled demo catalog; optional Google Places/Routes |
| 10 | Build process & testing | 8 phases; 62 tests; CI; the camelCase bug; the 'request is not a function' bug caught by browser QA |
| 11 | Contributions | CRediT-style, per member |
| 12 | Lessons & limitations | Honesty architecture; image models garble words; browser QA matters; limitations + future |

## Demo flow (slides 5–6, live if possible)

1. Homepage → Plan My Night
2. Fill the form (Denver · Sat · 6 people · $60 · dinner + games + drinks · walking · "one vegetarian")
3. Generate → walk the itinerary (venues, times, travel, budget)
4. Chat: "Make dinner cheaper" / "We finish by 10 PM" → show only what you asked changes
5. 🔁 Swap / 🔒 Lock + 🎲 Regenerate
6. Save, Copy for group chat, Share link, Surprise Me
7. 🎨 Poster → modal with the exact prompt; 🔊 Hear it → the night reads itself
8. Close with the honesty line: *"the app never pretends — every pick, number, and artifact is checkable."*

## Backup answers (Q&A)

- **What if the AI fails?** 3 retries, then a top-rated fallback that tells you in the notes.
- **Real users?** Works now; Google keys swap in via `.env` with zero code changes.
- **How is it tested?** 62 automated tests (offline) + CI + independent QA + browser click-through (evidence in `docs/evidence/`).
- **Demo-mode places?** Labeled "sample places" until a Google Places key is configured — by design.
