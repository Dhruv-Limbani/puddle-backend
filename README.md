# Puddle Backend — Development Progress

This README captures the current scaffold and progress so we can pick up immediately next time.

## Current status (what's implemented)

- Project scaffold created under `app/` with modules:
	- `app/core/` — `config.py`, `db.py` (async SQLAlchemy engine and session)
	- `app/models/` — SQLAlchemy ORM models (`models.py`) that try to use Postgres-specific types (UUID, JSONB, pgvector) when available and fall back for local dev
	- `app/schemas/` — Pydantic schemas for Vendors, Buyers, Agents, Datasets, DatasetColumns
	- `app/crud/` — CRUD helpers for vendors, buyers, agents, datasets, dataset_columns
	- `app/api/v1/routes/` — FastAPI routes for `vendors`, `buyers`, `agents`, `datasets`, and `dataset-columns` (registered under `/api/v1`)
	- `app/utils/embedding_utils.py` — embedding integration using `google-genai` (Gemini) with a safe fallback to a zero-vector

- FastAPI entrypoint: `app/main.py` (CORS, includes `api/v1` router, creates tables at startup using SQLAlchemy metadata)
- `.env` template created at project root (fill values before running)
- Dependency installation was run (`uv add ...`) and core packages were installed into the active virtualenv: FastAPI, Uvicorn, SQLAlchemy, asyncpg, aiosqlite, Alembic, pgvector, google-genai, python-dotenv, httpx, pytest, pytest-asyncio, and more.

## Files changed / added (high level)

- `app/main.py` — register `api/v1` router and DB table creation on startup
- `app/core/config.py` — reads `DATABASE_URL`, `GEMINI_API_KEY`, `OPENAI_API_KEY` from `.env`
- `app/core/db.py` — async engine and session
- `app/models/models.py` — ORM models with optional Postgres types
- `app/schemas/*` — Pydantic schemas for modules
- `app/crud/*` — CRUD helpers for modules
- `app/api/v1/routes/*` — API route implementations
- `app/utils/embedding_utils.py` — Gemini embedding integration with fallback
- `.env` — template (fill this before running against Postgres)

## How to continue (pick up here next time)

1. Fill the `.env` file at the project root with real secrets and DB connection. Example:

```
DATABASE_URL=postgresql+asyncpg://<db_user>:<db_pass>@<db_host>:5432/<db_name>
GEMINI_API_KEY=<your_gemini_api_key>
OPENAI_API_KEY=
```

2. If you haven't already, activate your virtualenv and ensure dependencies are installed. The project used `uv` to install packages. Example (if you need to re-run):

```bash
# activate venv (example)
source .venv/bin/activate
# install packages with uv
uv add fastapi 'uvicorn[standard]' sqlalchemy asyncpg aiosqlite alembic pgvector python-dotenv google-genai httpx pytest pytest-asyncio pytest-cov sqlalchemy-utils
```

3. Run the app for local development (creates tables from SQLAlchemy models on startup):

```bash
uvicorn app.main:app --reload --port 8000
```

4. API endpoints to test (prefix `/api/v1`):

- `POST /api/v1/vendors/` — create vendor
- `GET /api/v1/vendors/` — list vendors
- `GET /api/v1/vendors/{id}` — get vendor
- `POST /api/v1/buyers/`, `GET /api/v1/buyers/`, etc.
- `POST /api/v1/datasets/` — creates dataset and auto-generates embedding (uses `GEMINI_API_KEY` if available)
- `POST /api/v1/datasets/search/embedding` — semantic search by query (top_k)

Example dataset create JSON:

```json
{
	"vendor_id": "<vendor_uuid>",
	"title": "Global Shipping Index Data 2023",
	"description": "Comprehensive dataset covering global maritime trade...",
	"domain": "logistics",
	"dataset_type": "tabular"
}
```

## Notes, assumptions & known gaps

- Models attempt to use `pgvector` and Postgres `UUID`/`JSONB` when available; if you run with SQLite, the code will fall back to JSON and string-based UUIDs.
- Embeddings: `app/utils/embedding_utils.py` tries to use the `google-genai` client and the `gemini-embedding-001` model. Set `GEMINI_API_KEY` in `.env`. The client API surface varies between package versions; if you hit errors, I can adapt the code with the exact client usage you prefer.
- Vector search currently computes cosine similarity in Python as a portable fallback. For production and performance you should enable Postgres + `pgvector` and use the vector operator in SQL (I can add an optimized path).
- Alembic is not yet configured and migrations are not present — next step should be adding Alembic and generating the initial migration.
- Basic tests are not yet added; I can add `pytest-asyncio` tests for core flows next.

Note about the SQL script in the repo:

- The file `database-creation-script.sql` included in this repository is provided for reference only and documents the expected database schema and indexes. It is NOT intended to be executed against your production database from this repo — your Postgres instance is pre-provisioned and managed externally. Do not run the SQL script unless you're intentionally provisioning a fresh database for development.


## Next steps (recommended)

1. Fill `.env` with `DATABASE_URL` and `GEMINI_API_KEY`.
2. Add Alembic config (`alembic/`, `alembic.ini`) and create the initial migration reflecting `app.models`.
3. Add tests under `app/tests/` (pytest-asyncio) and run them.
4. Implement pgvector-optimized vector search SQL path and add indexes (ivfflat) via migration.
5. Harden production settings (CORS origins, logging, secrets management).

If you want, I can implement steps 2–4 now. Reply with which item you want me to do next and I will proceed and update the repo.

---
Updated: Please refer to the repository commit history — code changes were applied to the `app/` package and `.env` template was created.

