"""
Runtime orchestrator -- drives the LangGraph DAG for a single analysis task.

The public entrypoint is ``run_dag()``, which is designed to be submitted as a
FastAPI ``BackgroundTask``.  It:

1. Builds the DAG (mock | real).
2. Seeds the initial ``AnalysisState``.
3. Opens a DB session.
4. Updates the task status to RUNNING and publishes a ``TaskStartEvent``.
5. Invokes the DAG via ``dag.ainvoke()``.
6. Persists the generated report and marks the task COMPLETED.
7. Catches any exception, marks the task FAILED, and publishes the error.
"""

import logging

from backend.api.routes.events import publish
from backend.config import settings
from backend.core.workflow import build_dag
from backend.db.crud import create_report, update_task_status
from backend.db.database import async_session
from backend.db.models import TaskStatus
from backend.schemas.events import (
    TaskCompleteEvent,
    TaskFailedEvent,
    TaskStartEvent,
    iso_now,
)

logger = logging.getLogger(__name__)


def get_initial_state(
    task_id: str,
    target_product: str,
    analysis_dimensions: list[str],
) -> dict:
    """Return the seed ``AnalysisState`` dict for a new DAG run."""
    return {
        "task_id": task_id,
        "target_product": target_product,
        "analysis_dimensions": analysis_dimensions,
        "search_queries": [],
        "analysis_plan": "",
        "raw_research": [],
        "structured_analysis": None,
        "final_report_markdown": "",
        "metric_cards": None,
        "quality_score": 0.0,
        "quality_feedback": "",
        "current_agent": "",
        "execution_logs": [],
        "token_usage": {},
        "llm_call_count": 0,
        "status": "RUNNING",
        "error": None,
    }


async def run_dag(
    task_id: str,
    target_product: str,
    analysis_dimensions: list[str],
) -> None:
    """Execute the full analysis DAG for a single task.

    This function is designed to be called as a FastAPI ``BackgroundTask``.
    It owns its own database session so it can outlive the request that
    spawned it.

    Args:
        task_id: UUID hex identifier of the task record.
        target_product: The product name being analysed.
        analysis_dimensions: The dimensions to evaluate (e.g.
            ``["功能分析", "定价策略"]``).
    """
    mock = settings.COMPETESCOPE_MOCK

    dag = build_dag(mock=mock)
    initial_state = get_initial_state(task_id, target_product, analysis_dimensions)

    async with async_session() as db:
        try:
            await update_task_status(db, task_id, TaskStatus.RUNNING)
            await publish(
                task_id,
                TaskStartEvent(
                    task_id=task_id,
                    target_product=target_product,
                    timestamp=iso_now(),
                ),
            )

            final_state = await dag.ainvoke(initial_state)

            report = await create_report(
                db,
                task_id=task_id,
                markdown=final_state["final_report_markdown"],
                structured=final_state.get("structured_analysis") or {},
                quality_score=final_state.get("quality_score", 0.0),
                token_usage=final_state.get("token_usage", {}),
            )
            await update_task_status(db, task_id, TaskStatus.COMPLETED)
            await publish(
                task_id,
                TaskCompleteEvent(
                    task_id=task_id,
                    report_id=report.id,
                    timestamp=iso_now(),
                ),
            )
        except Exception as e:
            logger.exception("DAG failed for task %s", task_id)
            await update_task_status(db, task_id, TaskStatus.FAILED, error=str(e))
            await publish(
                task_id,
                TaskFailedEvent(
                    task_id=task_id, error=str(e), timestamp=iso_now(),
                ),
            )
