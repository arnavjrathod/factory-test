# Smoke Report — code editor theme (cdf run)

**Date:** 2026-08-31
**Branch state:** detached HEAD in cdf worktree, base commit `220c5c6` ("Apply code editor dark theme to UI")
**Role:** smoke test only — no feature changes.

## What was verified

The two prior commits (`88b06ac`, `220c5c6`) already restyled the UI as a
code editor (VS Code Dark+–like palette). This run booted the app and
verified the happy path end-to-end, including the themed UI being served.

### 1. Quality gate

- `uv run pytest -W error` → **28 passed, 0 warnings** ✅

### 2. API boot + happy path (uvicorn on :8000, fresh SQLite DB)

| Check | Result |
|---|---|
| `GET /health` | 200 `{"status":"ok"}` ✅ |
| `GET /docs` (OpenAPI UI) | 200 ✅ |
| `POST /categories` (`work`) | 201-style success, id=1 ✅ |
| `POST /tasks` (title, high priority, category, due date) | created, id=1, `overdue:true` ✅ |
| `GET /tasks/1` | returns task ✅ |
| `PATCH /tasks/1` `status=done` | `overdue` flips to `false` ✅ |
| `GET /tasks?status=done&page=1&page_size=5` | paginated envelope (`items/total/page/page_size/total_pages`) ✅ |
| `GET /categories` | paginated ✅ |
| `POST /tasks` missing `title` | 422 with structured FastAPI validation detail ✅ |
| `DELETE /tasks/1` | 200 ✅ |

### 3. UI build + theme verification

- `cd ui && bun install && bun run build` → vite build succeeded
  (`dist/index.html` + CSS 6.64 kB + JS 151 kB, 32 modules). ✅
- After rebuilding `ui/dist`, the FastAPI static mount serves the SPA:
  `GET /` → 200 HTML (`<title>To-Do</title>`), assets served. ✅
- Built CSS contains the code-editor theme tokens:
  - background `#1e1e1e` (editor dark), surface `#252526` (sidebar),
    border `#3e3e42` ✅
  - syntax-like accents: keyword/blue `#569cd6`, function/yellow
    `#dcdcaa`, type/teal `#4ec9b0`, comment/green `#6a9955`,
    number `#b5cea8` ✅
  - font stack monospace (Consolas, SF Mono, Monaco, …) ✅

## Notes

- `ui/dist` is gitignored (build artifact); the theme source of truth is
  `ui/src/styles.css` + `ui/src/App.jsx`, both already committed.
- The `app.mount("/", ...)` for `ui/dist` is evaluated at import time, so
  the server must be (re)started *after* `ui/dist` exists for the SPA to
  be served. Observed during this run and documented here.
- No source changes were made in this run; the only new file is this
  report.

## Verdict

**PASS** — API happy path, quality gate, UI build, and served themed UI all
verified.
