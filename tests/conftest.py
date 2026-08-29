"""Shared test fixtures: isolated temp database per test session."""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient

# Point the app at a temp database before importing it.
_tempdir = tempfile.mkdtemp()
os.environ["TODO_DB_PATH"] = os.path.join(_tempdir, "test_todo.db")

from app.main import app  # noqa: E402
from app.database import database  # noqa: E402


@pytest.fixture()
def client():
    database.initialize()
    # Start each test with a clean database.
    with database.session() as conn:
        conn.execute("DELETE FROM tasks")
        conn.execute("DELETE FROM categories")
        conn.execute(
            "DELETE FROM sqlite_sequence WHERE name IN ('tasks', 'categories')"
        )
    with TestClient(app) as c:
        yield c
