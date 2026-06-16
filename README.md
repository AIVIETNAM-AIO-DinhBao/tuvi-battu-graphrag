# TuVi / BaTu GraphRAG

MVP web app for creating Tu Vi and Bat Tu charts, storing them in Supabase,
and later using the saved chart as context for GraphRAG chat.

## Project Layout

```text
backend/      FastAPI backend, Tu Vi engine, RAG placeholders
frontend/     Next.js app, auth pages, Bat Tu API route
infra/        Supabase and Neo4j schema files
data/         Local Tu Vi / Bat Tu source documents
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
Bat Tu: POST /api/battu/calculate
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

Bat Tu request shape:

```json
{
  "year": 1990,
  "month": 1,
  "day": 15,
  "hour": 14,
  "gender": "male",
  "label": "My chart"
}
```

The UI form keeps `birth_date` and `birth_time`; the frontend adapter derives
`year`, `month`, `day`, and `hour` for the Bat Tu endpoint.

Bat Tu currently supports years `1930-2048`, matching the local date mapping
data used by the calculator.

## Supabase Chart Storage Contract

Create-chart flow inserts one row into `la_so`:

```text
user_id
label
birth_date
birth_time
gender
chart_system   TUVI | BATU | TUVI_BATU
chart_data
chart_version
```

For `TUVI_BATU`, store combined chart data as:

```json
{
  "tuvi": { "chart_type": "TUVI", "version": "1.0" },
  "batu": { "chart_type": "BATU", "version": "1.0" }
}
```

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
