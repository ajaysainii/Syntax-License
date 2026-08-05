#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_VENV="$BACKEND_DIR/.venv"
BACKEND_PORT="${BACKEND_PORT:-8100}"
FRONTEND_PORT="${FRONTEND_PORT:-3100}"
API_BASE_URL="${API_BASE_URL:-http://127.0.0.1:${BACKEND_PORT}/api/v1}"

cleanup() {
  jobs -p | xargs -r kill >/dev/null 2>&1 || true
}

trap cleanup EXIT INT TERM

if [[ ! -f "$BACKEND_DIR/.env" && -f "$BACKEND_DIR/.env.example" ]]; then
  cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
fi

if [[ ! -f "$FRONTEND_DIR/.env.local" && -f "$FRONTEND_DIR/.env.example" ]]; then
  cp "$FRONTEND_DIR/.env.example" "$FRONTEND_DIR/.env.local"
fi

cat >"$FRONTEND_DIR/.env.local" <<EOF
NEXT_PUBLIC_API_BASE_URL=$API_BASE_URL
EOF

if [[ ! -d "$BACKEND_VENV" ]]; then
  python3 -m venv "$BACKEND_VENV"
fi

source "$BACKEND_VENV/bin/activate"
pip install -r "$BACKEND_DIR/requirements.txt"

pushd "$BACKEND_DIR" >/dev/null
"$BACKEND_VENV/bin/python" seed.py
"$BACKEND_VENV/bin/uvicorn" app.main:app --host 0.0.0.0 --port "$BACKEND_PORT" --reload &
popd >/dev/null

pushd "$FRONTEND_DIR" >/dev/null
npm install
NEXT_PUBLIC_API_BASE_URL="$API_BASE_URL" npx next dev --port "$FRONTEND_PORT" &
popd >/dev/null

echo "Backend:  http://127.0.0.1:$BACKEND_PORT"
echo "Frontend: http://127.0.0.1:$FRONTEND_PORT"
echo "Docs:     http://127.0.0.1:$BACKEND_PORT/docs"

wait
