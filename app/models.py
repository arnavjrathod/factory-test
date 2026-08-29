"""Pydantic schemas for request validation and response serialization."""

import datetime as dt
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


# ---- Categories ----

class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = None


class Category(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: str


# ---- Tasks ----

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.todo
    priority: TaskPriority = TaskPriority.medium
    due_date: Optional[dt.date] = None
    category_id: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[dt.date] = None
    category_id: Optional[int] = None


class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[dt.date] = None
    category_id: Optional[int] = None
    created_at: str
    updated_at: str
    overdue: bool = False


# ---- Pagination ----

class PaginatedTasks(BaseModel):
    items: list[Task]
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginatedCategories(BaseModel):
    items: list[Category]
    total: int
    page: int
    page_size: int
    total_pages: int


class Message(BaseModel):
    detail: str
