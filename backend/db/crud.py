"""
Async CRUD helpers for the CompeteScope database layer.

Each function accepts an ``AsyncSession`` as the first argument and
operates on the ORM models defined in ``backend.db.models``.
"""

import uuid
from datetime import UTC
from datetime import datetime

from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import Report
from backend.db.models import Task
from backend.db.models import TaskStatus

# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------


async def create_task(
    db: AsyncSession,
    target_product: str,
    analysis_dimensions: list[str],
) -> Task:
    """Create a new analysis task in PENDING status."""
    task = Task(
        id=uuid.uuid4().hex,
        target_product=target_product,
        analysis_dimensions=analysis_dimensions,
        status=TaskStatus.PENDING,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_task(
    db: AsyncSession,
    task_id: str,
) -> Task | None:
    """Fetch a single task by its hex ID, or None if not found."""
    return await db.get(Task, task_id)


async def list_tasks(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[Task], int]:
    """Return a paginated list of tasks ordered by creation time (newest
    first) together with the total count."""
    # total count
    count_q = select(func.count(Task.id))
    total_result = await db.execute(count_q)
    total: int = total_result.scalar_one()

    # page
    rows_q = (
        select(Task)
        .order_by(Task.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    rows_result = await db.execute(rows_q)
    rows = list(rows_result.scalars().all())

    return rows, total


async def update_task_status(
    db: AsyncSession,
    task_id: str,
    status: TaskStatus,
    error: str | None = None,
) -> None:
    """Update a task's status and (optionally) error message.

    When *status* is ``COMPLETED`` the ``completed_at`` timestamp is set
    automatically.
    """
    task = await db.get(Task, task_id)
    if task is None:
        raise ValueError(f"Task {task_id!r} not found")

    task.status = status
    task.error = error
    if status == TaskStatus.COMPLETED:
        task.completed_at = datetime.now(UTC)

    await db.commit()


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


async def create_report(
    db: AsyncSession,
    task_id: str,
    markdown: str | None = None,
    structured: dict | None = None,
    quality_score: float | None = None,
    token_usage: dict | None = None,
) -> Report:
    """Create a report linked to the given task."""
    report = Report(
        id=uuid.uuid4().hex,
        task_id=task_id,
        markdown_content=markdown,
        structured_data=structured,
        quality_score=quality_score,
        token_usage=token_usage,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


async def get_report(
    db: AsyncSession,
    report_id: str,
) -> Report | None:
    """Fetch a single report by its hex ID, or None if not found."""
    return await db.get(Report, report_id)
