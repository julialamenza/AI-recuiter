# AI recruiting lifecycle assistant (MVP)

FastAPI backend, React (Vite) frontend, PostgreSQL, and OpenAI agents for CV/JD structuring and screening. **Rejections are never automatic**: recording a reject requires an explicit human confirmation in the API and UI.

## Prerequisites

- Python 3.11+
- Node.js 20+ (or 22.12+ if using Vite 8+)
- Docker (for PostgreSQL)
- OpenAI API key

## Commands (quick reference)

**PostgreSQL**

```bash
docker compose up -d postgres
docker compose ps
docker compose down
```

**Backend — first-time setup** (from repository root)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

**Backend — migrations and API** (`cd backend`, venv activated)

```bash
export DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/recruiting
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend — tests**

```bash
cd backend && source .venv/bin/activate && pytest tests/ -q
```

**Frontend** (`cd frontend`)

```bash
npm install
npm run dev
npm run build
npm run preview
```

## 1. Start PostgreSQL

```bash
docker compose up -d postgres
```

Wait until healthy (`docker compose ps`).

## 2. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Create `backend/.env` from the root [`.env.example`](.env.example) (set `OPENAI_API_KEY`).

Run migrations:

```bash
export DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/recruiting
alembic upgrade head
```

Start API:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- OpenAPI: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

## 3. Frontend

```bash
cd frontend
cp ../.env.example .env
# Edit .env: VITE_API_BASE_URL=http://localhost:8000
npm install
npm run dev
```

Open `http://localhost:5173`.

## 4. Typical flow

1. **Availability** — Set weekly hours and timezone (used for slot proposals).
2. **Jobs** — Create a job; the backend structures requirements with OpenAI.
3. **Candidates** — Upload a CV (PDF/DOCX/text); profile fields are extracted with OpenAI.
4. **Screening** — Pick candidate + job; get score, reasons, markdown summary, and AI **suggestion** only.
5. **Decision** — Shortlist or manual review freely; **Reject** requires the confirmation modal.
6. **Interview slots** — Generate proposed times from your saved availability.

## Project layout

- [`backend/app/api/`](backend/app/api/) — HTTP routers (thin).
- [`backend/app/services/`](backend/app/services/) — Persistence and orchestration (human-gate for reject).
- [`backend/app/agents/`](backend/app/agents/) — OpenAI calls only (no DB).
