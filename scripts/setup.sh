#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== CompeteScope — Setup ==="

# ----- Backend -----
echo ""
echo "[1/4] Setting up Python backend..."
cd "$ROOT/backend"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  echo "  Virtual environment created."
fi

source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate 2>/dev/null
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "  Python dependencies installed."

# ----- Environment -----
echo ""
echo "[2/4] Setting up environment variables..."
if [ ! -f "$ROOT/.env" ]; then
  cp "$ROOT/.env.example" "$ROOT/.env"
  echo "  .env created from .env.example. Edit it with your keys."
else
  echo "  .env already exists — skipped."
fi

# ----- Frontend -----
echo ""
echo "[3/4] Setting up Node.js frontend..."
cd "$ROOT/frontend"

if command -v bun &> /dev/null; then
  bun install --frozen-lockfile 2>/dev/null || bun install
  echo "  Frontend dependencies installed (bun)."
else
  npm install
  echo "  Frontend dependencies installed (npm)."
fi

# ----- Done -----
echo ""
echo "[4/4] Setup complete."
echo ""
echo "  Start backend:  cd $ROOT && source backend/.venv/bin/activate && uvicorn backend.main:app --reload"
echo "  Start frontend: cd frontend && npm run dev"
echo ""
echo "  Health check:   http://localhost:8000/api/health"
echo "  Frontend:       http://localhost:3000"
