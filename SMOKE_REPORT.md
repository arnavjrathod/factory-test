# Smoke Report — Theme Switcher (light / neon dark)

- **Date:** 2026-09-02
- **Commit under test:** `39f8fca` ("Add light/neon dark theme switcher to UI")
- **Role:** smoke test only — no feature changes made.

## Result: PASS (with one environment limitation, see below)

## What was verified

### 1. Test suite (AGENTS.md quality gate)

```
uv run pytest -W error
28 passed in 0.21s
```

All backend tests pass with warnings treated as errors.

### 2. Backend booted and happy path exercised

Server: `uv run uvicorn app.main:app --port 8000` → started cleanly.

| Check | Result |
|---|---|
| `GET /health` | `200 {"status":"ok"}` |
| `GET /docs` (OpenAPI UI) | `200` |
| `POST /categories` (`smoke`) | `200`, id 1 returned |
| `POST /tasks` (title + priority=high + category) | `200`, `overdue:false` |
| `GET /tasks` (pagination) | `200`, paginated envelope `{items,total,page,page_size,total_pages}` |
| `PATCH /tasks/1` → `status:"done"` | `200`, status updated |
| `DELETE /tasks/1`, `DELETE /categories/1` | `200` / `200` |
| Validation: `POST /tasks` with empty title | structured `{"detail":[...]}` error |

Test data was cleaned up (task + category deleted). Server stopped after the run.

### 3. Theme switcher implementation (code inspection)

The switcher ships in commit `39f8fca`:

- `ui/src/App.jsx` — `theme` state initialized from `localStorage.theme`,
  falling back to `prefers-color-scheme` (default `light`); a `useEffect`
  applies `document.body.dataset.theme` and persists to localStorage; a
  `🌙/☀️` toggle button in the header flips `light` ⇄ `dark` with proper
  `aria-label`/`title` for accessibility.
- `ui/src/styles.css` — `body[data-theme="dark"]` overrides all CSS custom
  properties (neon cyan/magenta accent `#00f0ff`/`#ff2bd6` on dark surfaces,
  glow shadows, adjusted badge/error styles); `button.theme-toggle` styled
  via the same variables so it adapts to both themes.

Logic reviewed: initialization, persistence, toggle, and CSS variable
coverage are correct and self-consistent. No backend code was touched by
the feature, consistent with the passing test suite.

## Environment limitation

The React UI could **not** be built or served in this environment: `ui/`
has no `node_modules`, and no `npm`/real `node` binary is available
(`node` is a Bun wrapper; `npm` not found). Therefore no browser-level
verification of the toggle click was possible. Verification of the theme
switcher is by code inspection (above) plus the full backend happy path.

## Minor observations (non-blocking, not fixed — smoke test only)

1. `ui/index.html` has no inline pre-hydration script to set
   `data-theme` before React mounts — users with a stored/dark preference
   may see a brief light-theme flash on load (App.jsx sets the attribute
   in `useEffect` immediately after mount).
2. `<meta name="theme-color" content="#4f6ef7">` is fixed and does not
   follow the active theme (cosmetic).
