#!/usr/bin/env bash

set -euo pipefail

APP_ROOT="${APP_ROOT:-/var/www/syntax-licensing}"
APP_USER="${APP_USER:-www-data}"
APP_GROUP="${APP_GROUP:-www-data}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"
BACKEND_SERVICE_NAME="${BACKEND_SERVICE_NAME:-syntax-licensing-backend}"
FRONTEND_SERVICE_NAME="${FRONTEND_SERVICE_NAME:-syntax-licensing-frontend}"
BACKEND_ENV_FILE="${BACKEND_ENV_FILE:-$APP_ROOT/backend/.env}"
FRONTEND_ENV_FILE="${FRONTEND_ENV_FILE:-$APP_ROOT/frontend/.env.production}"
DOMAIN="${DOMAIN:-lcs.syntaxnation.com}"

BACKEND_DIR="$APP_ROOT/backend"
FRONTEND_DIR="$APP_ROOT/frontend"
BACKEND_VENV="$BACKEND_DIR/.venv"

require_file() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    echo "Missing required file: $path" >&2
    exit 1
  fi
}

require_command() {
  local name="$1"
  if ! command -v "$name" >/dev/null 2>&1; then
    echo "Missing required command: $name" >&2
    exit 1
  fi
}

require_command python3
require_command npm
require_command systemctl
require_file "$BACKEND_ENV_FILE"
require_file "$FRONTEND_ENV_FILE"
require_file "$BACKEND_DIR/requirements.txt"
require_file "$FRONTEND_DIR/package.json"

mkdir -p "$BACKEND_VENV"
python3 -m venv "$BACKEND_VENV"
source "$BACKEND_VENV/bin/activate"
pip install --upgrade pip
pip install -r "$BACKEND_DIR/requirements.txt"

pushd "$BACKEND_DIR" >/dev/null
set -a
source "$BACKEND_ENV_FILE"
set +a
alembic upgrade head
python seed.py
popd >/dev/null

pushd "$FRONTEND_DIR" >/dev/null
npm install
set -a
source "$FRONTEND_ENV_FILE"
set +a
npm run build
popd >/dev/null

cat >/etc/systemd/system/"$BACKEND_SERVICE_NAME".service <<EOF
[Unit]
Description=Syntax Licensing FastAPI Backend
After=network.target mysql.service

[Service]
Type=simple
User=$APP_USER
Group=$APP_GROUP
WorkingDirectory=$BACKEND_DIR
EnvironmentFile=$BACKEND_ENV_FILE
ExecStart=$BACKEND_VENV/bin/uvicorn app.main:app --host 127.0.0.1 --port $BACKEND_PORT
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

cat >/etc/systemd/system/"$FRONTEND_SERVICE_NAME".service <<EOF
[Unit]
Description=Syntax Licensing Next.js Frontend
After=network.target

[Service]
Type=simple
User=$APP_USER
Group=$APP_GROUP
WorkingDirectory=$FRONTEND_DIR
EnvironmentFile=$FRONTEND_ENV_FILE
Environment=PORT=$FRONTEND_PORT
ExecStart=/usr/bin/npm run start -- --hostname 127.0.0.1 --port $FRONTEND_PORT
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable "$BACKEND_SERVICE_NAME" "$FRONTEND_SERVICE_NAME"
systemctl restart "$BACKEND_SERVICE_NAME" "$FRONTEND_SERVICE_NAME"

cat <<EOF
Deployment complete.

Backend service:  $BACKEND_SERVICE_NAME
Frontend service: $FRONTEND_SERVICE_NAME
Expected domain:  $DOMAIN

Verify:
  systemctl status $BACKEND_SERVICE_NAME
  systemctl status $FRONTEND_SERVICE_NAME
  journalctl -u $BACKEND_SERVICE_NAME -n 100 --no-pager
  journalctl -u $FRONTEND_SERVICE_NAME -n 100 --no-pager
EOF

