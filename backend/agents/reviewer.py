"""
Reviewer Agent -- evaluates the quality of the generated report and produces
a quality score together with actionable feedback.

MVP note: only mock mode is implemented.  Both mock and real paths return
a fixed quality score of 0.85.
"""

import asyncio

from backend.api.routes.events import publish
from backend.core.state import AnalysisState
from backend.schemas.events import AgentStartEvent, AgentCompleteEvent, iso_now


async def run_reviewer(state: AnalysisState, mock: bool = True) -> dict:
    task_id = state["task_id"]

    await publish(
        task_id,
        AgentStartEvent(task_id=task_id, agent="reviewer", timestamp=iso_now()),
    )

    if mock:
        await asyncio.sleep(1)

    await publish(
        task_id,
        AgentCompleteEvent(
            task_id=task_id,
            agent="reviewer",
            timestamp=iso_now(),
            duration_ms=1000,
            output_summary="质量评分: 0.85",
        ),
    )

    return {
        "quality_score": 0.85,
        "quality_feedback": "报告内容完整，结构清晰，SWOT 分析逻辑合理。",
        "current_agent": "reviewer",
    }
