"""Data-access layer (repository pattern).

The routers only talk to repositories through this abstract interface, so the
storage backend can be swapped out in the future without touching the API.
"""

import abc
import datetime as dt
from typing import Optional

from app.database import Database
from app.models import TaskPriority, TaskStatus

PRIORITY_RANK = {"low": 0, "medium": 1, "high": 2}


class AbstractTaskRepository(abc.ABC):
    @abc.abstractmethod
    def list(
        self,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        category_id: Optional[int] = None,
        sort: Optional[str] = None,
        order: str = "asc",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict], int]: ...

    @abc.abstractmethod
    def get(self, task_id: int) -> Optional[dict]: ...

    @abc.abstractmethod
    def create(self, data: dict) -> dict: ...

    @abc.abstractmethod
    def update(self, task_id: int, data: dict) -> Optional[dict]: ...

    @abc.abstractmethod
    def delete(self, task_id: int) -> bool: ...

    @abc.abstractmethod
    def clear_category(self, category_id: int) -> None: ...


class AbstractCategoryRepository(abc.ABC):
    @abc.abstractmethod
    def list(self, page: int = 1, page_size: int = 20) -> tuple[list[dict], int]: ...

    @abc.abstractmethod
    def get(self, category_id: int) -> Optional[dict]: ...

    @abc.abstractmethod
    def create(self, data: dict) -> dict: ...

    @abc.abstractmethod
    def update(self, category_id: int, data: dict) -> Optional[dict]: ...

    @abc.abstractmethod
    def delete(self, category_id: int) -> bool: ...


class SQLiteTaskRepository(AbstractTaskRepository):
    """SQLite-backed task repository."""

    def __init__(self, db: Database) -> None:
        self.db = db

    @staticmethod
    def _is_overdue(row: dict) -> bool:
        due = row.get("due_date")
        if not due or row.get("status") == TaskStatus.done.value:
            return False
        try:
            return dt.date.fromisoformat(due) < dt.date.today()
        except ValueError:
            return False

    def _decorate(self, row: dict) -> dict:
        row = dict(row)
        row["overdue"] = self._is_overdue(row)
        return row

    def list(
        self,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        category_id: Optional[int] = None,
        sort: Optional[str] = None,
        order: str = "asc",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict], int]:
        where, params = [], []
        if status is not None:
            where.append("status = ?")
            params.append(status.value)
        if priority is not None:
            where.append("priority = ?")
            params.append(priority.value)
        if category_id is not None:
            where.append("category_id = ?")
            params.append(category_id)

        where_sql = f" WHERE {' AND '.join(where)}" if where else ""

        # Sorting (FR-05): due_date asc/desc and priority.
        order = "desc" if order == "desc" else "asc"
        if sort == "due_date":
            # Overdue-first behavior is left to clients; NULLs sort last.
            order_sql = (
                f" ORDER BY due_date IS NULL, due_date {order.upper()}, id ASC"
            )
        elif sort == "priority":
            # High priority first on asc (most useful), reverse on desc.
            direction = "DESC" if order == "asc" else "ASC"
            order_sql = (
                f" ORDER BY CASE priority WHEN 'high' THEN 2 WHEN 'medium' THEN 1"
                f" ELSE 0 END {direction}, id ASC"
            )
        else:
            order_sql = " ORDER BY id ASC"

        with self.db.session() as conn:
            total = conn.execute(
                f"SELECT COUNT(*) FROM tasks{where_sql}", params
            ).fetchone()[0]
            offset = (page - 1) * page_size
            rows = conn.execute(
                f"SELECT * FROM tasks{where_sql}{order_sql} LIMIT ? OFFSET ?",
                [*params, page_size, offset],
            ).fetchall()

        items = [self._decorate(dict(r)) for r in rows]
        return items, total

    def get(self, task_id: int) -> Optional[dict]:
        with self.db.session() as conn:
            row = conn.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
        return self._decorate(dict(row)) if row else None

    def create(self, data: dict) -> dict:
        fields = {
            "title": data["title"],
            "description": data.get("description"),
            "status": data.get("status", TaskStatus.todo.value),
            "priority": data.get("priority", TaskPriority.medium.value),
            "due_date": data.get("due_date"),
            "category_id": data.get("category_id"),
        }
        with self.db.session() as conn:
            cursor = conn.execute(
                "INSERT INTO tasks (title, description, status, priority,"
                " due_date, category_id) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    fields["title"],
                    fields["description"],
                    fields["status"],
                    fields["priority"],
                    fields["due_date"],
                    fields["category_id"],
                ),
            )
            task_id = cursor.lastrowid
            row = conn.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
        return self._decorate(dict(row))

    def update(self, task_id: int, data: dict) -> Optional[dict]:
        updates, params = [], []
        for column in ("title", "description", "status", "priority",
                       "due_date", "category_id"):
            if column in data and data[column] is not None:
                value = data[column]
                if isinstance(value, TaskStatus):
                    value = value.value
                elif isinstance(value, TaskPriority):
                    value = value.value
                elif hasattr(value, "isoformat"):
                    value = value.isoformat()
                updates.append(f"{column} = ?")
                params.append(value)
        if not updates:
            return self.get(task_id)
        updates.append("updated_at = datetime('now')")
        params.append(task_id)
        with self.db.session() as conn:
            cursor = conn.execute(
                f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?", params
            )
            if cursor.rowcount == 0:
                return None
            row = conn.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
        return self._decorate(dict(row))

    def delete(self, task_id: int) -> bool:
        with self.db.session() as conn:
            cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            return cursor.rowcount > 0

    def clear_category(self, category_id: int) -> None:
        """Detach all tasks from the given category (sets category_id NULL)."""
        with self.db.session() as conn:
            conn.execute(
                "UPDATE tasks SET category_id = NULL WHERE category_id = ?",
                (category_id,),
            )


class SQLiteCategoryRepository(AbstractCategoryRepository):
    """SQLite-backed category repository."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def list(self, page: int = 1, page_size: int = 20) -> tuple[list[dict], int]:
        with self.db.session() as conn:
            total = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
            rows = conn.execute(
                "SELECT * FROM categories ORDER BY id ASC LIMIT ? OFFSET ?",
                (page_size, (page - 1) * page_size),
            ).fetchall()
        return [dict(r) for r in rows], total

    def get(self, category_id: int) -> Optional[dict]:
        with self.db.session() as conn:
            row = conn.execute(
                "SELECT * FROM categories WHERE id = ?", (category_id,)
            ).fetchone()
        return dict(row) if row else None

    def create(self, data: dict) -> dict:
        with self.db.session() as conn:
            cursor = conn.execute(
                "INSERT INTO categories (name, description) VALUES (?, ?)",
                (data["name"], data.get("description")),
            )
            category_id = cursor.lastrowid
            row = conn.execute(
                "SELECT * FROM categories WHERE id = ?", (category_id,)
            ).fetchone()
        return dict(row)

    def update(self, category_id: int, data: dict) -> Optional[dict]:
        updates, params = [], []
        for column in ("name", "description"):
            if column in data and data[column] is not None:
                updates.append(f"{column} = ?")
                params.append(data[column])
        if updates:
            params.append(category_id)
            with self.db.session() as conn:
                cursor = conn.execute(
                    f"UPDATE categories SET {', '.join(updates)} WHERE id = ?",
                    params,
                )
                if cursor.rowcount == 0:
                    return None
        return self.get(category_id)

    def delete(self, category_id: int) -> bool:
        """Delete a category. Associated tasks keep existing with
        category_id = NULL (FR-04, enforced by ON DELETE SET NULL)."""
        with self.db.session() as conn:
            cursor = conn.execute(
                "DELETE FROM categories WHERE id = ?", (category_id,)
            )
            return cursor.rowcount > 0
