# Smoke Test Report

**Date:** 2026-08-29
**Role:** Smoke tester (boot check + happy-path verification)
**Result:** ✅ PASS — all checks green, no fixes required

## What was run

| Step | Command | Result |
|------|---------|--------|
| Dependency resolution (Python) | `uv sync` | ✅ synced into `.venv` |
| Test suite (quality gate) | `uv run pytest -W error` | ✅ 28 passed, 0 warnings |
| Dependency resolution (UI) | `cd ui && npm install` | ✅ installed |
| UI production build | `cd ui && npm run build` | ✅ 32 modules, `dist/` emitted (~6.4 kB CSS, ~151 kB JS) |
| Backend boot | `uv run uvicorn app.main:app --port 8000` | ✅ started cleanly |
| Health check | `GET /health` | ✅ `{"status":"ok"}` |
| UI served | `GET /` | ✅ HTTP 200, `<title>To-Do</title>` |

## Happy path (API, against running server)

1. `POST /categories` `{"name":"smoke"}` → created (id 1)
2. `POST /tasks` with title/description/priority/category → created (`status=todo`, `overdue=false`)
3. `PATCH /tasks/1` `{"status":"done"}` → status transitioned
4. `GET /tasks?status=done` → paginated list, `total=1`
5. `DELETE /tasks/1`, `DELETE /categories/1` → both 200

All responses were structured JSON as documented; no errors in `/tmp/uvicorn.log`.

## UI task aspect (gradients / glow / readability)

The stylesheet (`ui/src/styles.css`, bundled into `dist/assets/index-*.css`)
already contains the requested styling, verified in the production build:

- **Gradients:** page background `linear-gradient(160deg, …)`, gradient header
  title (background-clip: text), gradient primary buttons, gradient task cards,
  gradient error banner. Verified present in built CSS.
- **Subtle glow:** accent/danger glow tokens (`--accent-glow`, `--glow`,
  `--glow-sm`), focus rings (`box-shadow: 0 0 0 3px`), hover glow on
  buttons/cards/task rows, overdue badge glow.
- **Readability:** antialiased text, 16px base font with 1.6 line-height,
  high-contrast text tokens, dimmed secondary text, hover lift on interactive
  rows, focus-visible states on all inputs.

## Notes

- Server was booted, exercised, and shut down cleanly.
- No code changes were needed; everything worked on first boot.
- Repo-wide quality gate (`uv run pytest -W error`) passes: **28/28**.
