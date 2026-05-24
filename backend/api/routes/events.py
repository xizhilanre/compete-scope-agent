"""SSE streaming route — in-memory asyncio.Queue, heartbeat, auto-cleanup.

Usage from agent nodes:
    from backend.api.routes.events import publish

    await publish(task_id, AgentStartEvent(...))
    await publish(task_id, ToolCallEvent(...))
    await publish(task_id, TaskCompleteEvent(...))
"""

import asyncio
import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from backend.schemas.events import (
    AgentCompleteEvent,
    AgentStartEvent,
    HeartbeatEvent,
    SSEEvent,
    TaskCompleteEvent,
    TaskFailedEvent,
    TaskStartEvent,
    ToolCallEvent,
    ToolResultEvent,
    iso_now,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["events"], prefix="/analyze")

HEARTBEAT_SECONDS = 30
QUEUE_SIZE = 256

# ---------------------------------------------------------------------------
# Global in-memory registry — no Redis/RabbitMQ
# ---------------------------------------------------------------------------

_sse_queues: dict[str, asyncio.Queue[SSEEvent]] = {}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def ensure_queue(task_id: str) -> asyncio.Queue[SSEEvent]:
    """Get or create the SSE queue for a task."""
    if task_id not in _sse_queues:
        _sse_queues[task_id] = asyncio.Queue(maxsize=QUEUE_SIZE)
    return _sse_queues[task_id]


async def publish(task_id: str, event: SSEEvent) -> None:
    """Push an event to a task's SSE queue. No-op if no listener is connected."""
    queue = _sse_queues.get(task_id)
    if queue is None:
        return
    try:
        queue.put_nowait(event)
    except asyncio.QueueFull:
        logger.warning("SSE queue full for task %s, dropping event %s", task_id, event.event)


def remove_queue(task_id: str) -> None:
    """Clean up the queue for a finished/disconnected task."""
    _sse_queues.pop(task_id, None)


# ---------------------------------------------------------------------------
# SSE endpoint
# ---------------------------------------------------------------------------

async def _event_generator(task_id: str) -> AsyncGenerator[str, None]:
    """Yield SSE-formatted strings from the task's event queue.

    Heartbeat: if no event arrives for HEARTBEAT_SECONDS, a heartbeat is sent.
    Cleanup: when task_complete/task_failed arrives, or the client disconnects,
    the queue is removed from the registry.
    """
    queue = ensure_queue(task_id)

    try:
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=HEARTBEAT_SECONDS)
            except asyncio.TimeoutError:
                heartbeat = HeartbeatEvent(task_id=task_id, timestamp=iso_now())
                yield _format_sse("heartbeat", heartbeat.model_dump_json())
                continue

            yield _format_sse(event.event, event.model_dump_json())

            if event.event in ("task_complete", "task_failed"):
                break
    except asyncio.CancelledError:
        logger.info("SSE stream cancelled for task %s", task_id)
    finally:
        remove_queue(task_id)
        logger.info("SSE queue cleaned up for task %s", task_id)


@router.get("/{task_id}/stream")
async def stream_events(task_id: str, request: Request) -> StreamingResponse:
    """SSE endpoint — client connects here to receive live analysis events.

    Open in browser / curl:
        curl -N http://localhost:8000/api/analyze/{task_id}/stream
    """
    return StreamingResponse(
        _event_generator(task_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# Simulated event stream (for smoke testing)
# ---------------------------------------------------------------------------

@router.post("/{task_id}/_simulate")
async def simulate_events(task_id: str) -> dict:
    """Fire a background task that publishes mock agent events to the SSE queue.

    Call this BEFORE connecting to GET /{task_id}/stream.
    """
    ensure_queue(task_id)

    async def _run():
        agents = ["planner", "research", "analysis", "writer", "reviewer"]
        tools = [
            ("tavily_search", {"query": "competitors"}),
            ("firecrawl_extract", {"url": "https://example.com"}),
        ]

        await asyncio.sleep(0.3)
        await publish(task_id, TaskStartEvent(
            task_id=task_id, target_product="Notion", timestamp=iso_now(),
        ))

        for agent in agents:
            await asyncio.sleep(0.3)
            await publish(task_id, AgentStartEvent(
                task_id=task_id, agent=agent, timestamp=iso_now(),
            ))

            for tool_name, tool_input in tools:
                await asyncio.sleep(0.15)
                await publish(task_id, ToolCallEvent(
                    task_id=task_id, agent=agent, tool_name=tool_name,
                    tool_input=tool_input, timestamp=iso_now(),
                ))
                await asyncio.sleep(0.1)
                await publish(task_id, ToolResultEvent(
                    task_id=task_id, agent=agent, tool_name=tool_name,
                    success=True, duration_ms=42, timestamp=iso_now(),
                ))

            await asyncio.sleep(0.2)
            await publish(task_id, AgentCompleteEvent(
                task_id=task_id, agent=agent, timestamp=iso_now(),
                duration_ms=500, output_summary=f"{agent} completed analysis",
            ))

        await asyncio.sleep(0.3)
        await publish(task_id, TaskCompleteEvent(
            task_id=task_id, timestamp=iso_now(),
            total_duration_ms=3500, report_id="r_smoke_001",
        ))

    asyncio.create_task(_run())
    return {"ok": True, "task_id": task_id, "message": "Simulation started — connect to SSE stream now"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _format_sse(event_name: str, data: str) -> str:
    """Build a single SSE message block."""
    return f"event: {event_name}\ndata: {data}\n\n"
