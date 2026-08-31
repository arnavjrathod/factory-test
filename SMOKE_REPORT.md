# Smoke Test Report — Code-Editor Theme

Run: cdf smoke test for the "make the UI theme look like a code editor" change.
Date: 2026-08-31 · Branch state: detached HEAD (cdf worktree) · Tester did NOT
implement features — verification only.

## Scope of the change under test

Commit `59c51ae` "Apply code-editor dark theme to UI" (predecessor stage):

- `ui/index.html` — font load update
- `ui/src/App.jsx` — theme-related class/markup tweaks
- `ui/src/styles.css` — full retheme:
  - Dark VS-Code-style palette: `--bg: #1e1e1e`, `--surface: #252526`,
    `--border: #3c3c3c`, `--text: #d4d4d4`, `--accent: #569cd6` (blue),
    `--danger: #f44747`, plus token colors (`--string`, `--function`,
    `--type`, `--variable`, `--comment`).
  - Monospace editor font stack: "Fira Code", "JetBrains Mono", "Cascadia
    Code", Consolas, Monaco, Courier New.
  - VS-Code-style selection color (`#264f78`), reduced radii (8px/4px).

## Verification steps and results

### 1. Backend boot — PASS

```
uv sync                          # deps installed into .venv
uv run uvicorn app.main:app --port 8000
```

Server started cleanly; `GET /health` → `200 {"status":"ok"}`.

### 2. API happy path (task + category lifecycle) — PASS

| Step | Request | Result |
|------|---------|--------|
| Create category | `POST /categories {"name":"smoke-test"}` | 201, id=1 |
| Create task | `POST /tasks {"title":"smoke happy path","category_id":1,"priority":"high","due_date":"2026-09-30"}` | 201, status=todo, overdue=false |
| Update | `PATCH /tasks/1 {"status":"done"}` | 200, status=done, updated_at bumped |
| Filter+list | `GET /tasks?status=done&page=1&page_size=5` | 200, total=1, item present |
| Delete task | `DELETE /tasks/1` | 200 |
| Delete category | `DELETE /categories/1` | 200 |
| Docs | `GET /docs` | 200 |

### 3. UI build (closest equivalent to booting the frontend) — PASS

```
cd ui && bun install && bun run build
```

- `vite v5.4.21` build succeeded, 32 modules transformed, no errors.
- `ui/dist/assets/index-*.css` confirmed to contain the new theme values
  (`#1e1e1e` and `Fira Code` present in the bundled CSS), i.e. the theme
  change is actually shipped in the production bundle.

### 4. Backend test suite — PASS

```
uv run pytest -W error
```

28 passed in 0.22s, no warnings-as-errors failures.

## Cleanup

- Test data (category + task) deleted via the API during the run.
- Scratch SQLite DB removed; `ui/dist` is gitignored.
- Uvicorn server stopped.
- `ui/bun.lock` is a byproduct of `bun install` (untracked); included in the
  commit for reproducibility.

## Verdict

**PASS.** The app boots, the full API happy path works, the frontend builds
with the code-editor theme in the final bundle, and the test suite is green.
No new features were implemented in this stage.
