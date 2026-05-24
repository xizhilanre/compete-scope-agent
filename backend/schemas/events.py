"""SSE event schemas — strongly typed, exact match with frontend types/sse-events.ts."""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# String literal unions
# ---------------------------------------------------------------------------

EventType = Literal[
    "task_start",
    "agent_start",
    "agent_complete",
    "tool_call",
    "tool_result",
    "task_complete",
    "task_failed",
    "heartbeat",
]

AgentName = Literal["planner", "research", "analysis", "writer", "reviewer"]

ALL_AGENTS: list[AgentName] = ["planner", "research", "analysis", "writer", "reviewer"]


# ---------------------------------------------------------------------------
# Individual event models
# ---------------------------------------------------------------------------

class TaskStartEvent(BaseModel):
    event: Literal["task_start"] = "task_start"
    task_id: str
    target_product: str
    timestamp: str


class AgentStartEvent(BaseModel):
    event: Literal["agent_start"] = "agent_start"
    task_id: str
    agent: AgentName
    timestamp: str


class AgentCompleteEvent(BaseModel):
    event: Literal["agent_complete"] = "agent_complete"
    task_id: str
    agent: AgentName
    timestamp: str
    duration_ms: int = 0
    output_summary: str = ""


class ToolCallEvent(BaseModel):
    event: Literal["tool_call"] = "tool_call"
    task_id: str
    agent: AgentName
    tool_name: str
    tool_input: dict = Field(default_factory=dict)
    timestamp: str


class ToolResultEvent(BaseModel):
    event: Literal["tool_result"] = "tool_result"
    task_id: str
    agent: AgentName
    tool_name: str
    success: bool
    duration_ms: int = 0
    timestamp: str


class TaskCompleteEvent(BaseModel):
    event: Literal["task_complete"] = "task_complete"
    task_id: str
    timestamp: str
    total_duration_ms: int = 0
    report_id: str = ""


class TaskFailedEvent(BaseModel):
    event: Literal["task_failed"] = "task_failed"
    task_id: str
    error: str
    timestamp: str


class HeartbeatEvent(BaseModel):
    event: Literal["heartbeat"] = "heartbeat"
    task_id: str
    timestamp: str


# ---------------------------------------------------------------------------
# Discriminated union — used for publish_event typing
# ---------------------------------------------------------------------------

SSEEvent = (
    TaskStartEvent
    | AgentStartEvent
    | AgentCompleteEvent
    | ToolCallEvent
    | ToolResultEvent
    | TaskCompleteEvent
    | TaskFailedEvent
    | HeartbeatEvent
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()
