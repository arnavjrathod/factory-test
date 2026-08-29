# AGENTS.md

## Quality gate (run before committing and before reporting completion)

```bash
uv run pytest -W error
```

All tests must pass with warnings treated as errors (CI treats warnings as
failures). Tests live in `tests/`; dependencies are managed with `uv`
(`pyproject.toml` + `uv.lock`, installed into `.venv` via `uv sync` — see
`make install`). Requires [uv](https://docs.astral.sh/uv/) on `$PATH`.

## Running the app

```bash
uv run uvicorn app.main:app --port 8000   # docs at http://localhost:8000/docs
```
