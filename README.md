# NightOut AI

**Less Planning. More Living.**

NightOut AI is a smart group night-out planner: tell it your city, budget, group
size, free time, and what you're into, and it builds a complete evening itinerary —
real places, honest price estimates, travel-aware timing, and an AI you can talk to
to change the plan on the fly.

Built for a graduate Generative AI course (MBAX 6418).

## Project status

| Phase | What | Status |
|---|---|---|
| 1 | Project setup, homepage, planning form, UI kit, responsive theme | ✅ Done |
| 2 | FastAPI backend, Google Places retrieval, demo-mode fallback | ✅ Done |
| 3 | AI itinerary generation, schema validation, itinerary UI | ✅ Done |
| 4 | Conversational itinerary editing, stop swap, cost/timing recalculation | ⏳ Next |
| 5 | Map + timeline, save/share | ⏳ |
| 6 | Tests, docs, polish | ⏳ |

See `BUILD_LOG.md` for the development story.

## Repository layout

```
final-project/
├── backend/            # FastAPI app (REST API)
│   ├── app/
│   │   ├── main.py     # app entry point
│   │   └── core/       # config / environment handling
│   ├── requirements.txt
│   └── .env.example    # all required environment variables, documented
├── frontend/           # React + Vite single-page app
│   ├── src/
│   │   ├── pages/      # Home, Planner
│   │   ├── components/ # UI kit, form, navbar
│   │   └── api/        # backend client
│   └── package.json
├── README.md           # this file
└── BUILD_LOG.md        # phases, decisions, bugs, lessons
```

## Running the app

### Backend (FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate        # Windows (git-bash): . .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env                 # add real keys as you configure them
uvicorn app.main:app --reload --port 8000
```

### Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev                          # opens http://localhost:5173
```

## Environment variables

Everything lives in `backend/.env` (see `.env.example`). Never commit real keys.

| Variable | Needed for |
|---|---|
| `OPENAI_API_KEY` | AI itinerary generation (OpenAI or any compatible endpoint) |
| `OPENAI_BASE_URL` | Optional: alternate OpenAI-compatible base URL |
| `OPENAI_MODEL` | Optional: model name override |
| `GOOGLE_PLACES_API_KEY` | Real venue retrieval (restaurants, bars, venues) |
| `GOOGLE_ROUTES_API_KEY` | Travel time / distance between stops |
| `TICKETMASTER_API_KEY` | Optional: live concerts / comedy / events |
| `ALLOWED_ORIGINS` | Comma-separated frontend origins for CORS |

**No API keys? The app runs in an explicitly-labeled demo mode** with sample
places — sample results are always labeled as such and never disguised as live data.

## Testing

`cd backend && pytest` — API and planning-logic tests (Phase 6 rounds these out).
