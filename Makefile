.PHONY: install test gate run

install:
	uv sync

test:
	uv run pytest

# Quality gate: tests must pass (warnings treated as errors by CI policy).
gate:
	uv run pytest -W error

run:
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
