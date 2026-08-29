# To-Do UI (React + Vite)

A small React UI for the To-Do REST API. It talks to the same endpoints
(`/tasks`, `/categories`) on the same origin.

## Layout

- Dependencies install into `ui/node_modules` (this directory is portable —
  copy/move the repo freely, no global installs needed).
- `npm run build` outputs to `ui/dist`, which FastAPI serves automatically
  at `/` (API routes always take precedence over the static mount).

## Development

```bash
# terminal 1 — backend
uv run uvicorn app.main:app --port 8000

# terminal 2 — frontend (proxies /tasks, /categories, /health to :8000)
cd ui && npm install && npm run dev   # http://localhost:5173
```

## Production

```bash
cd ui && npm install && npm run build
uv run uvicorn app.main:app --port 8000   # UI at http://localhost:8000/
```

## Features

- Create, edit, delete, and check off tasks
- Filter by status, priority, category; sort by due date/priority
- Pagination
- Category management (create/delete; deleting keeps tasks)
- Overdue highlighting
