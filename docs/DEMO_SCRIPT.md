# NightOut AI — Live Demo Script (~4 minutes)

Use this as your walkthrough for the class presentation. Everything here is the
REAL app running locally (backend :8000 + frontend :5173). No mockups.

---

## 0. Before you present (2 minutes of setup)

```bash
cd Desktop/final-project
# terminal 1 — backend
cd backend && .venv/Scripts/python.exe -m uvicorn app.main:app --port 8000   # Windows
cd backend && .venv/bin/python -m uvicorn app.main:app --port 8000           # Mac / Linux
# terminal 2 — frontend
cd frontend && npm run dev
```

Open **http://localhost:5173** in a browser, maximize, maybe zoom to 100–110 %.

---

## 1. The promise (0:00–0:40) — homepage

"Every group knows the pain: 47 messages, 12 restaurant links, and still no
plan. **NightOut AI** fixes that — you answer a few questions, and it builds
the whole night in seconds."

- Show the homepage: **"Less Planning. More Living."**
- Click **Plan My Night**.

## 2. The form (0:40–1:10)

"It's just one form — and it covers the things that actually break group plans."

- Fill: Denver CO · next Saturday · group of 6 · **$60/person**
- Activities: **Dinner + Games & arcade bars + Casual drinks**
- Time: 7:00 PM → 11:30 PM · Walking
- Notes: *"one vegetarian, keep it fun"*

*(Tip: the budget slider + presets and the activity chips show you built real
UX, not a homework form. The live "Your night so far" panel updates as you type.)*

## 3. The AI builds the night (1:10–1:50)

Click **✨ Generate My Night Out** — the loading overlay runs ~10 seconds.

Walk the result, top to bottom:

1. **Mini-map** — "Every stop plotted on its real coordinates, no API key
   needed; one click opens the full Google Maps route with all stops."
2. **Stop cards** — real venues, prices, travel minutes between stops, and the
   AI's reason: *"this spot handles the group's vegetarian"* — the model
   couldn't invent this place; it picked from venues we actually retrieved.
3. **Budget box** — "$46 of $60 — $14 left per person."

## 4. The killer feature: change it by talking (1:50–3:10)

"Now the part that makes it feel alive — you edit the night like you're
texting the group."

- Type: **"Make dinner cheaper"** → only dinner changes ($20 → $18), rest kept.
- Type: **"We want to finish by 10 PM now"** → same places, new times; the
  last stop drops *with a note explaining why* (it couldn't fit before 10).
- Type: **"Swap the bar for dessert"** → drinks become Little Man Ice Cream.
- Demo the **🔁 Swap this stop** button and **🔒 Lock** on a card too:
  "Lock dinner, regenerate — dinner survives."

## 5. Save, share, wrap (3:10–3:50)

- **💾 Save** the night, then **📋 Copy for group chat**: "Here's the plan —
  ready to paste into the actual group chat."
- **🎲 Surprise me** on a fresh form: "And if the group can't agree on
  anything — the app just plans a great night anyway."

Close with the honesty one-liner:

> "One thing I built deliberately: the app never pretends. The AI can only
> choose from venues we actually retrieved, every number comes from venue data
> not the model, budgets are hard limits, and sample data is labeled — demo
> mode says 'sample places' right in the UI until you connect live APIs."

## Backup answers

- **"What if the AI fails?"** → 3 retries, then a top-rated fallback that tells
  you in the notes. The app never breaks.
- **"Is this ready for real users?"** → the full flow works now; live Google
  Places/Routes keys swap in via `.env` — retrieval, travel times, and photos
  go live with zero code changes.
- **"How is it tested?"** → 49 automated tests including budget invariants,
  duplicate-venue guards, chronological schedules, and AI-output parsers.
