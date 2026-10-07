# GovJobs Intelligence Platform

This repository now includes a working MVP implementation for the evidence-backed public-sector recruitment intelligence platform described in the PRD and architecture documents.

## Included artifacts

- `PRD.md` — product requirements and platform scope
- `API_SPEC.md` — API contract for the MVP
- `schema.sql` — canonical PostgreSQL schema for recruitment, evidence, and profile data
- `backend/` — FastAPI service implementing recruitment search, profile logic, saved jobs, reminders, evidence-backed assistant responses, and deterministic eligibility evaluation
- `frontend/` — Next.js starter for the public dashboard, plus a Python-served fallback UI at the backend root route

## Backend startup

```bash
cd backend
$env:PYTHONPATH='.'
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Then open:
- http://127.0.0.1:8000/ for the dashboard
- http://127.0.0.1:8000/v1/recruitments for the recruitment API

## Validation

```bash
cd backend
$env:PYTHONPATH='.'
pytest tests/test_api.py -q
```

## Design principles implemented

- official-source-first data modeling
- structured recruitment + evidence records
- deterministic eligibility evaluation
- candidate profile matching
- reminders and saved-job tracking
- assistant answers with citation metadata
- clear separation between evidence and AI explanations
