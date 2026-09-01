# Smoke Report — Theme Switcher (Light/Dark Mode)

Date: 2026-09-01
Branch state: detached HEAD, commit `189093e` ("Add light/dark theme switcher")
Role: smoke test only — no feature changes made in this run.

## Scope

Verify the happy path for the newly added light/dark theme switcher:

- Backend theme preference API (`GET /theme`, `POST /theme`)
- Frontend theme bootstrap + toggle in the built React UI
- Regression: existing API tests still pass

## Quality gate

```
uv run pytest -W error
.................................  [100%]
33 passed in 0.44s
```

All tests pass with warnings treated as errors, including the new
`tests/test_ui.py` (theme cookie default, set dark, invalid value → 422,
UI HTML theme script markers).

## Boot + happy path verification

Server: `uv run uvicorn app.main:app --port 8123`

| Check | Result |
|---|---|
| `GET /health` | 200 `{"status":"ok"}` |
| `GET /theme` (no cookie) | 200 `{"theme":"light"}` (default) |
| `POST /theme {"theme":"dark"}` | 200 `{"theme":"dark"}` + `Set-Cookie: theme=dark; Max-Age=31536000` |
| `GET /theme` with `Cookie: theme=dark` | 200 `{"theme":"dark"}` (cookie respected) |
| `POST /theme {"theme":"blue"}` | 422 (invalid theme rejected) |
| `GET /` after building UI | 200, served HTML contains `data-theme`, `localStorage`, `prefers-color-scheme` bootstrap script |

Frontend build: `cd ui && bun install && bun run build` — succeeded
(`dist/index.html` 0.97 kB, CSS 7.6 kB, JS 152 kB). The built UI includes:

- Inline head script that sets `data-theme` from `localStorage` or the
  `prefers-color-scheme` media query (no flash of wrong theme)
- `ui/styles/light.css` and `ui/styles/dark.css` CSS-variable theme sheets
- `useTheme()` hook in `ui/src/App.jsx` with a toggle button
  (`🌙 Dark` / `☀️ Light`, accessible `aria-label`), persisting the choice
  to `localStorage`

## Notes / observations

- `GET /` returns 404 until `ui/dist` is built; the static mount is
  optional by design (API-first). After `bun run build` the UI serves
  correctly. Build artifacts are gitignored.
- Theme persistence is client-side (`localStorage`) only; the
  `/theme` cookie endpoints are exposed as a server-side preference hook
  but are not yet read by the React app. Not a blocker for the happy path.

## Verdict

✅ PASS — happy path works end to end; quality gate green.
