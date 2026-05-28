"""Task routes -- CRUD the analysis job lifecycle.

All endpoints are wired to the real database layer and the DAG runtime.
"""

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.runtime import run_dag
from backend.db.crud import create_task as create_task_db
from backend.db.crud import get_task, list_tasks as list_tasks_crud
from backend.db.database import get_db
from backend.schemas.base import err, ok
from backend.schemas.task import TaskCreateRequest, TaskListResponse, TaskResponse

router = APIRouter(tags=["tasks"], prefix="/tasks")


@router.post("", status_code=201)
async def create_task(
    body: TaskCreateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Create a new competitive analysis task and enqueue it for execution."""
    task = await create_task_db(db, body.target_product, body.analysis_dimensions)
    background_tasks.add_task(
        run_dag, task.id, task.target_product, task.analysis_dimensions
    )
    return ok(TaskResponse.model_validate(task))


@router.get("")
async def list_tasks(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List analysis tasks with pagination (newest first)."""
    items, total = await list_tasks_crud(db, skip, limit)
    return ok(
        TaskListResponse(
            total=total,
            skip=skip,
            limit=limit,
            items=[TaskResponse.model_validate(t) for t in items],
        )
    )


@router.get("/{task_id}")
async def get_task_route(task_id: str, db: AsyncSession = Depends(get_db)):
    """Get a single task by its hex ID."""
    task = await get_task(db, task_id)
    if not task:
        return err("任务不存在")
    return ok(TaskResponse.model_validate(task))
