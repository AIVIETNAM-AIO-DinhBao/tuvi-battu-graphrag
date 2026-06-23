# TuVi GraphRAG

MVP web app for creating Tử Vi charts, storing them in Supabase, and later
using the saved chart as context for GraphRAG chat.

## Project Layout

```text
backend/      FastAPI backend, Tu Vi engine, RAG placeholders
frontend/     Next.js app, auth pages, chart creation flow
infra/        Supabase and Neo4j schema files
data/         Local Tu Vi source documents
docs/         Project notes
```

## Environment

Create the root `.env` file and fill in the values needed by your local setup:

```powershell
copy .env.example .env
```

Common variables are for Supabase, Neo4j, Langfuse, and Gemini. Frontend public
Supabase variables should be placed in `frontend/.env.local` when needed:

```text
NEXT_PUBLIC_SUPABASE_URL=...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
```

Environment files are ignored by git.

## Backend Setup

From the repo root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
```

Install the Tu Vi engine wrapper dependencies:

```powershell
cd backend
.\setup_lasotuvi.ps1
```

On Linux/macOS/WSL, use:

```bash
cd backend
chmod +x setup_lasotuvi.sh
./setup_lasotuvi.sh
```

If Windows prints `execvpe(/bin/bash) failed`, use the PowerShell script above;
that error means WSL/bash is not available.

Run the backend:

```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

If your shell has the venv activated, this shorter form is fine:

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

Backend checks:

```powershell
cd backend
python -c "from app.main import app; print('OK')"
python -m pytest tests/test_lasotuvi_service.py tests/test_tuvi_engine.py -v
```

## Frontend Setup

From `frontend/`:

```powershell
npm install
npm run build
npm run dev
```

The dev server runs at:

```text
http://localhost:3000
```

`frontend/.next/` and `frontend/tsconfig.tsbuildinfo` are generated build/cache
artifacts and should not be committed.

## Chart Engine Endpoints

Public endpoints used by the create-chart flow:

```text
Tu Vi:  POST <FASTAPI_BASE_URL>/chart/tuvi
```

`POST /lasotuvi/generate` is a low-level diagnostic endpoint for the raw
lasotuvi wrapper. Do not use it for the chart creation UI.

Tu Vi request shape:

```json
{
  "label": "My chart",
  "birth_date": "1990-01-15",
  "birth_time": "14:30",
  "gender": "male"
}
```

## Supabase Chart Storage Contract

Create-chart flow inserts one row into `la_so`:

```text
user_id
label
birth_date
birth_time
gender
chart_system   TUVI
chart_data
chart_version
```

`chart_system` is kept for compatibility, but the MVP accepts only `TUVI`.
Store the normalized Tử Vi engine response directly in `chart_data`, with
`chart_version = "tuvi-v1"`.

See `backend/docs/chart-schema.md` for the locked contract used by
`W2-ENGINE-04`.

## Useful Scripts

```powershell
python scripts/apply_supabase_schema.py
python scripts/apply_neo4j_schema.py
```

These scripts read connection settings from `.env`.

## Git Notes

Generated files are ignored:

```text
frontend/.next/
frontend/tsconfig.tsbuildinfo
.pytest_cache/
pytest-cache-files-*/
```

If these files were already tracked before `.gitignore` was updated, untrack
them once without deleting local files:

```powershell
git rm -r --cached frontend/.next
git rm --cached frontend/tsconfig.tsbuildinfo
```

Then commit the `.gitignore` update and the removal from git tracking.
