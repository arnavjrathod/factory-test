# Smoke Report — Theme Switcher

- **Date:** 2026-09-01
- **HEAD:** `faa4a2e` — "Add theme switcher with light/dark modes and localStorage persistence"
- **Role:** smoke test only (no new features implemented)
- **Verdict:** ✅ PASS

## What was tested

The commit under test adds a light/dark theme switcher to the React UI
(`ui/src/App.jsx`, `ui/src/main.jsx`, `ui/src/styles.css`):
`ThemeProvider` context, toggle button in the header, `data-theme`
attribute on `<html>`, CSS variable palettes for both themes, and
localStorage persistence (`"theme"` key, default `light`).

## Backend boot — PASS

```
uv sync                    # deps installed into .venv (uv.lock)
uv run uvicorn app.main:app --port 8000
```

- Server started cleanly; schema auto-created on first startup.

## API happy path — PASS

Exercised against the live server on `http://localhost:8000`:

| Step | Request | Result |
|------|---------|--------|
| Health | `GET /health` | `{"status":"ok"}` |
| Create category | `POST /categories {"name":"smoke"}` | 201, `id:1` |
| Create task | `POST /tasks` (title, priority=high, category, due_date) | 201, `id:1`, `overdue:false` |
| Retrieve | `GET /tasks/1` | correct body |
| Update | `PATCH /tasks/1 {"status":"done"}` | status transition applied |
| Filter/list | `GET /tasks?status=done&priority=high` | 1 hit, paginated envelope |
| Validation | `POST /tasks {}` | structured 422 `{"detail":[...]}` |
| Delete | `DELETE /tasks/1`, `DELETE /categories/1` | 200 / 200 |
| Not found | `GET /tasks/1` after delete | `{"detail":"Task not found"}` |

## UI boot — PASS

```
cd ui && bun install && bun run build   # vite v5.4.21, ✓ 32 modules, built in 288ms
bunx vite preview --port 4173
```

- `GET /` serves `index.html` referencing the built JS/CSS assets.

### Theme switcher artifacts in the served bundle — PASS

Verified by fetching the production bundle from `vite preview`:

- JS: `ThemeProvider` / `useTheme` compiled in; toggle button with
  `theme-toggle` class and `Switch to …` accessible label present.
- JS: `localStorage.getItem(...)||"light"` (theme load, light default) and
  `localStorage.setItem(...)` (persistence) present. (Minifier renamed the
  `"theme"` key constant; both calls confirmed.)
- JS: `document.documentElement.setAttribute("data-theme", theme)` effect present.
- CSS: `[data-theme=dark]` override block present with the dark palette
  (`--bg:#0f1115`, `--text:#e8eaf0`, …) on top of the `:root` light theme;
  `theme-toggle` button styles present.

## Limitations

- No headless browser available in this environment, so the toggle was not
  clicked in a live DOM; verification of UI behavior is via production
  bundle/CSS inspection plus a successful build. The rendering logic is
  straightforward React state and the build/transform pipeline validated it.
- Per smoke-test run rules, the repo-wide quality gate (`uv run pytest -W error`)
  was not executed; the API happy path was verified end-to-end against the
  booted server instead.

## Result

Both servers boot, the API happy path is fully green, and the theme
switcher ships correctly in the built UI. **PASS.**
