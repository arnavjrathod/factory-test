"""FastAPI dependency providers.

Repositories are resolved through these functions, so swapping the storage
backend only requires changing what they construct.
"""

from app.database import Database, database
from app.repository import (
    AbstractCategoryRepository,
    AbstractTaskRepository,
    SQLiteCategoryRepository,
    SQLiteTaskRepository,
)

# Type aliases for dependency injection / easy swapping.
TaskRepository = AbstractTaskRepository
CategoryRepository = AbstractCategoryRepository


def get_database() -> Database:
    return database


def get_task_repository() -> TaskRepository:
    """Return the task repository (swap the class here to change storage)."""
    return SQLiteTaskRepository(database)


def get_category_repository() -> CategoryRepository:
    return SQLiteCategoryRepository(database)
