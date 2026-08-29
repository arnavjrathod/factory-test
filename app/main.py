"""Application entry point.

Run with:  uvicorn app.main:app --reload
"""

import contextlib
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import database
from app.routers import categories, tasks


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """Create the database schema automatically on first run."""
    database.initialize()
    yield


app = FastAPI(
    title="To-Do API",
    version="1.0.0",
    description=(
        "A lightweight task management REST API: create tasks, organize them "
        "with categories, priorities and due dates, filter/sort/paginate, "
        "and track completion."
    ),
    lifespan=lifespan,
)


app.include_router(tasks.router)
app.include_router(categories.router)


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok"}


# Serve the built React UI (ui/dist) if present. This mount is added last,
# so the API routes above always take precedence. See ui/README.md.
_UI_DIST = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ui", "dist"
)
if os.path.isdir(_UI_DIST):
    app.mount("/", StaticFiles(directory=_UI_DIST, html=True), name="ui")
