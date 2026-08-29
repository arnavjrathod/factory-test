"""Database connection management.

The schema is created automatically on first use (FR: reliability —
startup with zero existing data must work gracefully).
"""

import os
import sqlite3
from contextlib import contextmanager

DEFAULT_DB_PATH = os.environ.get("TODO_DB_PATH", "todo.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'todo'
        CHECK (status IN ('todo', 'in_progress', 'done')),
    priority TEXT NOT NULL DEFAULT 'medium'
        CHECK (priority IN ('low', 'medium', 'high')),
    due_date TEXT,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_category ON tasks(category_id);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
"""


class Database:
    """Thin wrapper around sqlite3 providing connections and schema setup."""

    def __init__(self, path: str = DEFAULT_DB_PATH) -> None:
        self.path = path
        self._initialized = False

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def initialize(self) -> None:
        """Create the schema if it does not exist yet (idempotent)."""
        conn = self.connect()
        try:
            with conn:
                conn.executescript(SCHEMA)
        finally:
            conn.close()
        self._initialized = True

    def ensure_initialized(self) -> None:
        if not self._initialized:
            self.initialize()

    @contextmanager
    def session(self):
        """Yield a connection with commit/rollback semantics."""
        self.ensure_initialized()
        conn = self.connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


# Application-wide database instance (path overridable via TODO_DB_PATH).
database = Database()
