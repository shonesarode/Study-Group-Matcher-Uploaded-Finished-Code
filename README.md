# Study Circle — Explainable Study Group Matcher

A runnable, privacy-conscious demo that matches students by shared classes, schedules, study goals, and meeting preferences. Python/FastAPI backend, lightweight responsive JavaScript frontend, deterministic ranking, tests, and CI.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8001
```

Open http://localhost:8001. API docs: http://localhost:8001/docs. Run tests with `pytest -q`.

## How matching works

1. Reject candidates without a shared class or time slot, or incompatible meeting formats.
2. Score shared classes (up to 50), availability (up to 30), compatible format (up to 10), and common study goals (up to 10).
3. Rank deterministically with human-readable explanations.
4. Suggest small groups using the intersection of everyone's available times.

## API

- `GET /api/options`: demo course, time, and goal choices
- `POST /api/matches`: ranked matches
- `POST /api/group`: compatible small group

