# To-Do API

A lightweight task management REST API (FastAPI + SQLite), implementing the
v1 product requirements: task CRUD, categories, priorities, due dates,
filtering/sorting, pagination and OpenAPI docs.

## Quick start

Requires [uv](https://docs.astral.sh/uv/) (installs Python deps into a local
`.venv` automatically — no global installs):

```bash
make install          # or: uv sync (creates .venv from uv.lock)
make run              # start server on http://localhost:8000
```

Or run commands directly with `uv run` (e.g. `uv run uvicorn app.main:app --port 8000`).

- Interactive docs: http://localhost:8000/docs
- Health check: `GET /health`

The SQLite schema is created automatically on first startup (no manual
migration step). Set `TODO_DB_PATH` to change the database location.

## API overview

| Method | Path                | Purpose                                        |
|--------|---------------------|------------------------------------------------|
| POST   | `/tasks`            | Create a task (only `title` required)          |
| GET    | `/tasks`            | List with filters, sorting and pagination      |
| GET    | `/tasks/{id}`       | Retrieve a task                                |
| PATCH  | `/tasks/{id}`       | Update any fields (free status transitions)    |
| DELETE | `/tasks/{id}`       | Delete a task                                  |
| POST   | `/categories`       | Create a category                              |
| GET    | `/categories`       | List categories (paginated)                    |
| GET    | `/categories/{id}`  | Retrieve a category                            |
| PATCH  | `/categories/{id}`  | Update a category                              |
| DELETE | `/categories/{id}`  | Delete (tasks survive, `category_id` → null)   |

### `GET /tasks` parameters

- **Filters:** `status`, `priority`, `category_id`
- **Sorting:** `sort=due_date|priority`, `order=asc|desc`
  (`sort=priority` ranks high → low on `asc`)
- **Pagination:** `page` (default 1), `page_size` (default 20, max 100)

Responses are paginated: `{ items, total, page, page_size, total_pages }`.
Tasks past their due date and not `done` carry `overdue: true`.

Errors always return structured JSON: `{ "detail": "..." }`.

## Architecture

- `app/main.py` — FastAPI app and startup (schema auto-creation)
- `app/models.py` — Pydantic request/response schemas (validation, FR-06)
- `app/repository.py` — repository pattern data layer (swappable storage)
- `app/database.py` — SQLite connection management + schema
- `app/routers/` — HTTP endpoints

## Tests / quality gate

```bash
make test   # or: make gate (adds -W error)
```

Dependencies are managed with [uv](https://docs.astral.sh/uv/): runtime deps in
`pyproject.toml` (`[project.dependencies]`), dev deps in the `[dependency-groups].dev`
group, pinned versions in the committed `uv.lock` for reproducible installs.
