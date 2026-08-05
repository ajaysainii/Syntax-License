# Syntax Licensing Platform

Production-oriented licensing platform for Syntax, targeting `lcs.syntaxnation.com`.

## Stack

- Next.js 15 + TypeScript admin portal
- FastAPI backend
- PostgreSQL for production, SQLite fallback for local quickstart
- SQLAlchemy + Alembic migrations
- Docker Compose deployment

## Features

- JWT-based admin authentication
- Customer and user management
- License issuance with hashed license keys at rest
- License status workflows: `active`, `suspended`, `revoked`, `expired`
- Device and installation tracking by `installation_id`
- Audit logging for admin operations and validation events
- Search and filter APIs for users, customers, and licenses
- Structured JSON request logs
- OpenAPI docs at `/docs`
- Seed script and pytest coverage for auth and validation flow

## Validation Endpoint

`POST /api/v1/licenses/validate`

Request:

```json
{
  "license_key": "SYNTAX-ABC123-DEF456-GHI789-JKL012",
  "installation_id": "device-001",
  "product": "syntax-cli",
  "version": "1.0.0",
  "hostname": "workstation",
  "platform": "darwin-arm64"
}
```

Response:

```json
{
  "valid": true,
  "status": "active",
  "message": "License is valid",
  "checked_at": "2026-08-05T10:00:00Z",
  "license": {
    "id": "uuid",
    "issued_to": "Jane Dev",
    "email": "jane@example.com",
    "plan": "pro",
    "expires_at": "2027-08-05T10:00:00Z",
    "features": ["offline-cache", "priority-support"],
    "status": "active"
  }
}
```

## Local Setup

1. Copy env files:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

2. Start with Docker Compose:

```bash
docker compose up --build
```

3. Seed initial data:

```bash
docker compose exec backend python seed.py
```

4. Access services:

- Frontend: `http://localhost:3000`
- Backend docs: `http://localhost:8000/docs`
- If you use `http://127.0.0.1:3000` instead, keep that origin in `CORS_ORIGINS`.

## Helper Scripts

- `scripts/local-run.sh`
  Starts backend and frontend together for local development, creating env files and a Python virtualenv if missing.
- `scripts/deploy-server.sh`
  Deploys to a Linux server that already has Nginx and MySQL installed, runs migrations and seed data, builds the frontend, and installs two `systemd` services.

Make them executable once:

```bash
chmod +x scripts/local-run.sh scripts/deploy-server.sh
```

Local run:

```bash
./scripts/local-run.sh
```

Server deploy example:

```bash
sudo APP_ROOT=/var/www/syntax-licensing \
BACKEND_ENV_FILE=/var/www/syntax-licensing/backend/.env \
FRONTEND_ENV_FILE=/var/www/syntax-licensing/frontend/.env.production \
APP_USER=www-data \
APP_GROUP=www-data \
./scripts/deploy-server.sh
```

For MySQL, set the database fields in `backend/.env` like:

```env
DB_ENGINE=mysql+pymysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=syntax_licensing
DB_USER=syntax_user
DB_PASSWORD=strong_password
```

If you want SQLite for local development, use:

```env
DB_ENGINE=sqlite
DB_NAME=syntax_license
```

## Manual Development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python seed.py
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Production Deployment

1. Provision PostgreSQL and point `DATABASE_URL` to the production instance.
2. Set strong `JWT_SECRET` and `LICENSE_HMAC_SECRET`.
3. Set `CORS_ORIGINS` to include `https://lcs.syntaxnation.com`.
4. Build and run the containers behind a reverse proxy:

```bash
docker compose -f docker-compose.yml up -d --build
```

5. Route:
- `lcs.syntaxnation.com` -> frontend container
- `/api/*` -> backend container

An example reverse proxy config is included at [deploy/nginx.conf](/Users/itaims/Projects/Syntax%20License%20/deploy/nginx.conf).

6. Run migrations on deploy:

```bash
docker compose exec backend alembic upgrade head
```

## Seed Credentials

- Email: `admin@syntaxnation.com`
- Password: `ChangeThisNow123!`

Change these immediately in production.
