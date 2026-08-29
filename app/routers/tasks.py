"""Task endpoints."""

import math
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app import models as schemas
from app.dependencies import (
    CategoryRepository,
    TaskRepository,
    get_category_repository,
    get_task_repository,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=schemas.PaginatedTasks)
def list_tasks(
    status: Optional[schemas.TaskStatus] = Query(default=None),
    priority: Optional[schemas.TaskPriority] = Query(default=None),
    category_id: Optional[int] = Query(default=None, ge=1),
    sort: Optional[str] = Query(
        default=None, description="Sort field: 'due_date' or 'priority'"
    ),
    order: str = Query(default="asc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    repo: TaskRepository = Depends(get_task_repository),
):
    """List tasks with filtering (FR-05), sorting (FR-05) and pagination (FR-07)."""
    if sort not in (None, "due_date", "priority"):
        raise HTTPException(
            status_code=422,
            detail="sort must be one of: due_date, priority",
        )
    items, total = repo.list(
        status=status,
        priority=priority,
        category_id=category_id,
        sort=sort,
        order=order,
        page=page,
        page_size=page_size,
    )
    return schemas.PaginatedTasks(
        items=[schemas.Task.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 0,
    )


@router.post("", response_model=schemas.Task, status_code=201)
def create_task(
    payload: schemas.TaskCreate,
    repo: TaskRepository = Depends(get_task_repository),
    category_repo: CategoryRepository = Depends(get_category_repository),
):
    """Create a task. Only `title` is required (FR-01)."""
    data = payload.model_dump()
    if data.get("category_id") is not None and category_repo.get(
        data["category_id"]
    ) is None:
        raise HTTPException(status_code=422, detail="Category does not exist")
    return repo.create(data)


@router.get("/{task_id}", response_model=schemas.Task)
def get_task(
    task_id: int,
    repo: TaskRepository = Depends(get_task_repository),
):
    task = repo.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=schemas.Task)
def update_task(
    task_id: int,
    payload: schemas.TaskUpdate,
    repo: TaskRepository = Depends(get_task_repository),
):
    """Update a task (US-04). Status may move freely between values (FR-02)."""
    data = payload.model_dump(exclude_unset=True)
    task = repo.update(task_id, data)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", response_model=schemas.Message)
def delete_task(
    task_id: int,
    repo: TaskRepository = Depends(get_task_repository),
):
    """Delete a task (US-05)."""
    if not repo.delete(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return schemas.Message(detail="Task deleted")
