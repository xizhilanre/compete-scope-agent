"""Task schemas — request validation & response serialization."""

import enum
from datetime import datetime

from pydantic import BaseModel
from pydantic import Field

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TaskStatusEnum(enum.StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

class TaskCreateRequest(BaseModel):
    target_product: str = Field(
        ...,
        min_length=1,
        max_length=500,
        examples=["Notion"],
        description="Product name to analyze",
    )
    analysis_dimensions: list[str] = Field(
        default_factory=lambda: ["功能分析", "定价策略", "SWOT分析", "市场定位"],
        description="Dimensions to evaluate",
    )


# ---------------------------------------------------------------------------
# Response — single task
# ---------------------------------------------------------------------------

class TaskResponse(BaseModel):
    id: str
    target_product: str
    analysis_dimensions: list
    status: TaskStatusEnum
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None
    report_id: str | None = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Response — paginated list
# ---------------------------------------------------------------------------

class TaskListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[TaskResponse]

    model_config = {"from_attributes": True}
