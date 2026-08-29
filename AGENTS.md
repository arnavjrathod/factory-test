# AGENTS.md

## Quality gate (run before committing and before reporting completion)

```bash
python3 -m pytest -W error
```

All tests must pass with warnings treated as errors (CI treats warnings as
failures). Tests live in `tests/`; dependencies in `requirements-dev.txt`.

## Running the app

```bash
uvicorn app.main:app --port 8000   # docs at http://localhost:8000/docs
```
