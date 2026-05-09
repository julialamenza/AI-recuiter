# AI recruiting lifecycle assistant (MVP)

FastAPI backend, React (Vite) frontend, PostgreSQL, and OpenAI agents for CV/JD structuring and screening. **Rejections are never automatic**: recording a reject requires an explicit human confirmation in the API and UI.

## Prerequisites

- Python 3.11+
- Node.js 20+ (or 22.12+ if using Vite 8+)
- Docker (for PostgreSQL)
- OpenAI API key (optional if you use **stub AI**; see [OpenAI and stub mode](#openai-and-stub-mode))

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
cp .env.example .env   # optional; leave VITE_API_BASE_URL unset for dev proxy
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

Create `backend/.env` from the root [`.env.example`](.env.example). See [OpenAI and stub mode](#openai-and-stub-mode) for when you can omit a key.

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

### OpenAI and stub mode

| Situation | What to set |
|-----------|----------------|
| **Real LLM** (CV/JD extraction, screening) | Set `OPENAI_API_KEY` in `backend/.env`. Optionally set `MOCK_AI=false` (default). |
| **No token / local smoke test** | Leave `OPENAI_API_KEY` empty. The backend uses **stub** structured data: uploads, jobs, and screenings still persist, but labels in the payload explain that no model ran. |
| **Force stubs even with a key** (e.g. CI) | Set `MOCK_AI=true`. |

OpenAI failures (quota, bad key, network) are returned as normal JSON errors with a `detail` field (not a generic HTML 500), so the UI can show the message.

## 3. Frontend

```bash
cd frontend
cp .env.example .env
# Optional: see "Frontend API URL" below
npm install
npm run dev
```

Open `http://localhost:5173`.

### Frontend API URL

- **Recommended for local dev:** Do **not** set `VITE_API_BASE_URL`, or leave it empty. The Vite dev server proxies `/api` to `http://127.0.0.1:8000` (see [`frontend/vite.config.ts`](frontend/vite.config.ts)), so the browser only talks to `http://localhost:5173` and you avoid cross-origin issues.
- **Different host (e.g. production):** Set `VITE_API_BASE_URL` to the full API origin (no trailing slash), for example `https://api.example.com`.

## 4. Typical flow

1. **Availability** — Set weekly hours and timezone (used for slot proposals).
2. **Jobs** — Create a job; the backend structures requirements with OpenAI (or **stub** data if there is no key or `MOCK_AI=true`).
3. **Candidates** — Upload a CV (PDF/DOCX/text); profile fields are extracted with OpenAI (or stubs under the same conditions).
4. **Screening** — Pick candidate + job; get score, reasons, markdown summary, and AI **suggestion** only (stubs return a fixed placeholder comparison when not using a real key).
5. **Decision** — Shortlist or manual review freely; **Reject** requires the confirmation modal.
6. **Interview slots** — Generate proposed times from your saved availability.

## Project layout

- [`backend/app/api/`](backend/app/api/) — HTTP routers (thin).
- [`backend/app/services/`](backend/app/services/) — Persistence and orchestration (human-gate for reject).
- [`backend/app/agents/`](backend/app/agents/) — OpenAI calls and stub fallbacks when there is no key or `MOCK_AI=true` (no DB).
