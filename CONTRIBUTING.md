# Contributing to NightOut AI

Thanks for helping build this! A few simple rules keep the app healthy and the
history clean. (Same pattern as a group project: branch → pull request → review.)

## Setup for new teammates

```bash
# 1. Clone the repo
git clone https://github.com/Marandacsmith96/nightout-ai.git
cd nightout-ai

# 2. Backend
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate   |  Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env        # then fill in YOUR OWN keys — never share the real one
uvicorn app.main:app --port 8000

# 3. Frontend (second terminal)
cd frontend
npm install
npm run dev                 # → http://localhost:5173
```

## The golden rules

1. **Never push to `main` directly.** Make a branch, open a pull request,
   someone reviews, then it merges.
2. **Never commit a real `.env`.** It is git-ignored on purpose. If you set up
   a new key, update `.env.example` with the NAME only (no value).
3. **Run the tests before pushing anything:**
   ```bash
   cd backend && python -m pytest -q     # expect: 49 passed
   cd frontend && npm run build          # expect: clean build
   ```
4. **Keep the docs honest.** If you change behavior, update `README.md` and
   add a line to `BUILD_LOG.md` — that file is the project's development story.

## Workflow (one small change at a time)

```bash
git checkout -b feature/your-initials-what        # e.g. feature/mc-cheaper-maps
# ...make your change...
git add -A && git commit -m "what and why"
git push -u origin feature/mc-cheaper-what
# open a Pull Request on GitHub → request a review → merge when green
```

## How the app is architected (read this before touching code)

- `backend/app/services/planner.py` — generation: retrieve → AI picks → validate
  → schedule → budget.
- `backend/app/services/editor.py` — conversational edits (interprets intent,
  applies it deterministically).
- `backend/app/services/ai.py` — the ONLY file that calls the language model.
  The model only ever picks from venue ids we retrieved — never invent places.
- `backend/app/schemas.py` — the API contract. **snake_case** (`group_size`).
  The frontend maps its camelCase to this via `frontend/src/lib/apiPlan.js` —
  change one, change the other, and keep the mapping in sync.
- Tests live in `backend/tests/` — invariants there (budget ≤ cap, no duplicate
  venues, chronological times) are the safety net. Don't weaken them.

## If something looks wrong

Open an issue with: what you clicked, what you expected, what happened, and the
browser console/backend log lines if any. Reproducible beats vague.
