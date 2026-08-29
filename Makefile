.PHONY: install test gate run

install:
	python3 -m pip install --user --break-system-packages -r requirements.txt -r requirements-dev.txt

test:
	python3 -m pytest

# Quality gate: tests must pass (warnings treated as errors by CI policy).
gate:
	python3 -m pytest -W error

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000
