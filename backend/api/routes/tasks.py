"""Task routes — CRUD the analysis job lifecycle.

MOCK DATA — all endpoints return static fixtures.
Replace with real DB queries after wiring up the repository layer.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Query

from backend.schemas.base import Envelope, err, ok
from backend.schemas.task import (
    TaskCreateRequest,
    TaskListResponse,
    TaskResponse,
    TaskStatusEnum,
)

router = APIRouter(tags=["tasks"], prefix="/tasks")

# ---------------------------------------------------------------------------
# Mock data
# ---------------------------------------------------------------------------

_MOCK_TASK = TaskResponse(
    id="a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6",
    target_product="Notion",
    analysis_dimensions={"pricing": True, "features": True, "ux": True, "market": True},
    status=TaskStatusEnum.COMPLETED,
    created_at=datetime(2026, 5, 24, 10, 0, 0, tzinfo=timezone.utc),
    updated_at=datetime(2026, 5, 24, 10, 9, 30, tzinfo=timezone.utc),
    started_at=datetime(2026, 5, 24, 10, 0, 1, tzinfo=timezone.utc),
    completed_at=datetime(2026, 5, 24, 10, 9, 30, tzinfo=timezone.utc),
    error=None,
)

_MOCK_TASKS = [
    _MOCK_TASK,
    TaskResponse(
        id="b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7",
        target_product="Figma",
        analysis_dimensions={"pricing": True, "features": True, "ux": True, "market": False},
        status=TaskStatusEnum.RUNNING,
        created_at=datetime(2026, 5, 24, 11, 0, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 5, 24, 11, 2, 0, tzinfo=timezone.utc),
        started_at=datetime(2026, 5, 24, 11, 0, 0, tzinfo=timezone.utc),
        completed_at=None,
        error=None,
    ),
]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("", response_model=Envelope[TaskResponse], status_code=201)
async def create_task(body: TaskCreateRequest) -> Envelope[TaskResponse]:
    """Create a new competitive analysis task."""
    task = TaskResponse(
        id="c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8",
        target_product=body.target_product,
        analysis_dimensions=body.analysis_dimensions,
        status=TaskStatusEnum.PENDING,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        started_at=None,
        completed_at=None,
        error=None,
    )
    return ok(task)


@router.get("", response_model=Envelope[TaskListResponse])
async def list_tasks(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> Envelope[TaskListResponse]:
    """List analysis tasks with pagination."""
    page = _MOCK_TASKS[skip : skip + limit]
    return ok(TaskListResponse(total=len(_MOCK_TASKS), skip=skip, limit=limit, items=page))


@router.get("/{task_id}", response_model=Envelope[TaskResponse])
async def get_task(task_id: str) -> Envelope[TaskResponse]:
    """Get a single task by ID."""
    if task_id == _MOCK_TASK.id:
        return ok(_MOCK_TASK)
    return err(f"Task {task_id!r} not found")
