#!/usr/bin/env bash
# NightOut AI — one-command dev startup.
#
# Boots the backend (FastAPI :8000) and the frontend (Vite :5173), creating
# the venv / node_modules / .env on the first run. Ctrl+C stops both.
#
# Requirements: Python 3.9+ and Node 18+ on PATH.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
info() { printf '\033[1;36m%s\033[0m\n' "$*"; }

# --- Backend (:8000) ---
if [ ! -d "$ROOT/backend/.venv" ]; then
  info "▸ Creating backend virtualenv…"
  python3 -m venv "$ROOT/backend/.venv"
fi
if [ ! -f "$ROOT/backend/.env" ]; then
  info "▸ Creating backend/.env from .env.example (add your keys later if you have them)"
  cp "$ROOT/backend/.env.example" "$ROOT/backend/.env"
fi
info "▸ Installing backend dependencies…"
"$ROOT/backend/.venv/bin/pip" install -q -r "$ROOT/backend/requirements.txt"
info "▸ Starting backend on http://localhost:8000 …"
(cd "$ROOT/backend" && .venv/bin/python -m uvicorn app.main:app --port 8000) &
BACK_PID=$!

# --- Frontend (:5173) ---
if [ ! -d "$ROOT/frontend/node_modules" ]; then
  info "▸ Installing frontend dependencies…"
  (cd "$ROOT/frontend" && npm install --silent)
fi
info "▸ Starting frontend on http://localhost:5173 …"
(cd "$ROOT/frontend" && npm run dev) &
FRONT_PID=$!

cleanup() {
  info "▸ Stopping servers…"
  kill "$BACK_PID" "$FRONT_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

info "✅ NightOut AI is ready →  http://localhost:5173"
info "   Backend health:       http://localhost:8000/api/health"
info "   Press Ctrl+C to stop both servers."
wait
