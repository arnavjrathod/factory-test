"""Category endpoints."""

import math

from fastapi import APIRouter, Depends, HTTPException, Query

from app import models as schemas
from app.dependencies import (
    CategoryRepository,
    TaskRepository,
    get_category_repository,
    get_task_repository,
)

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=schemas.PaginatedCategories)
def list_categories(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    repo: CategoryRepository = Depends(get_category_repository),
):
    items, total = repo.list(page=page, page_size=page_size)
    return schemas.PaginatedCategories(
        items=[schemas.Category.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 0,
    )


@router.post("", response_model=schemas.Category, status_code=201)
def create_category(
    payload: schemas.CategoryCreate,
    repo: CategoryRepository = Depends(get_category_repository),
):
    try:
        return repo.create(payload.model_dump())
    except Exception:
        raise HTTPException(
            status_code=422, detail="Category name must be unique"
        )


@router.get("/{category_id}", response_model=schemas.Category)
def get_category(
    category_id: int,
    repo: CategoryRepository = Depends(get_category_repository),
):
    category = repo.get(category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.patch("/{category_id}", response_model=schemas.Category)
def update_category(
    category_id: int,
    payload: schemas.CategoryUpdate,
    repo: CategoryRepository = Depends(get_category_repository),
):
    category = repo.update(category_id, payload.model_dump(exclude_unset=True))
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.delete("/{category_id}", response_model=schemas.Message)
def delete_category(
    category_id: int,
    repo: CategoryRepository = Depends(get_category_repository),
    task_repo: TaskRepository = Depends(get_task_repository),
):
    """Delete a category. Associated tasks are kept and their category_id
    is set to null (FR-04)."""
    if not repo.delete(category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    # Defensive: schema uses ON DELETE SET NULL, but ensure it even if
    # foreign keys are disabled.
    task_repo.clear_category(category_id)
    return schemas.Message(detail="Category deleted")
