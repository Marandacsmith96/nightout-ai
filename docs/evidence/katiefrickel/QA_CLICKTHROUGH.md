# QA click-through — real browser (Issue #3), 2026-11-11

Run by Katie via a scripted real-browser pass against the app running locally
(backend :8000 with class AI/FLUX/TTS keys, labeled demo-mode places; frontend
:5173). Addresses QA_REPORT.md's "Not yet tested" list.

## ✅ Verified in the browser (screenshots in `docs/screenshots/`)

| Item | Result |
|---|---|
| Itinerary restore from share link | Auto-restores plan + itinerary from the URL fragment |
| 🎨 Poster button | Real FLUX call → modal with the poster, caption overlay, exact prompt shown, download link |
| 🔊 Hear it button | Real Chatterbox call → modal with audio player + exact narration + download |
| 🔁 Swap this stop | **Found & fixed a real bug** — see below; after the fix the venue swaps via `/api/plan/edit` |
| 🔒 Lock + 🎲 Regenerate | Locked venue value preserved at index 0 after regeneration (API-level guarantee re-confirmed); the 🔒 chip rendering after a regenerate is worth one human tap during demo rehearsal |
| Mobile viewport (390px) | 0 px horizontal overflow on the form **and** the itinerary (screenshots: `mobile.png`) |

## 🐛 Bug found: conversational edits dead in the browser

Swap/Regenerate/chat edits never reached the backend. Root cause:
`frontend/src/api/client.js` `editNight` destructured its argument as
`request`, shadowing the module-level `request()` helper →
`TypeError: request is not a function` before any fetch. Fix committed
(`request: plan` rename) and re-verified live: edit POST fires, venue swaps,
honest-fallback note renders when the AI's JSON is unparseable. See
BUILD_LOG.md hotfix entry.

## ⚠️ Harness limitations (why some checks are API/reported, not clicked)

- The scripted browser's media pipeline cannot decode **any** audio (even a
  valid WAV), so playback itself is unverifiable here. However, `afinfo`
  decodes the Chatterbox MP3 cleanly (15.8 s, 128 kbps, 657 packets) and the
  MIME type is now sniffed from magic bytes, so playback in a normal browser
  is expected. One human play-click during rehearsal is recommended.
- Synthetic clicks worked for state-only buttons (Lock) and — after the fix —
  for edit buttons; the edit fix was verified by observing the fetch + backend
  log + DOM change, not just visual state.

## Not re-tested here

- Live Google Places/Routes mode (no key available locally) — optional;
  demo mode is the professor's expected path.
