"""
SQLAlchemy 2.0 async ORM models for CompeteScope.

Tables:
    tasks           — Analysis job lifecycle
    reports         — Generated competitive analysis output (1:1 with tasks)
    execution_logs  — Per-agent execution trace for observability
"""

import enum
import uuid
from datetime import UTC
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from backend.db.database import Base

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TaskStatus(enum.StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _utcnow() -> datetime:
    return datetime.now(UTC)


def _new_id() -> str:
    return uuid.uuid4().hex


# ---------------------------------------------------------------------------
# Task — analysis job
# ---------------------------------------------------------------------------

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(
        String(32), primary_key=True, default=_new_id, comment="UUID hex (32 chars)"
    )
    target_product: Mapped[str] = mapped_column(
        String(500), nullable=False, comment="Product name to analyze"
    )
    analysis_dimensions: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=dict, comment="e.g. {pricing: true, features: true}"
    )
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name="task_status_enum", create_type=True),
        nullable=False,
        default=TaskStatus.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    report: Mapped["Report | None"] = relationship(
        back_populates="task", uselist=False, lazy="selectin"
    )
    execution_logs: Mapped[list["ExecutionLog"]] = relationship(
        back_populates="task", lazy="selectin", order_by="ExecutionLog.id"
    )

    def __repr__(self) -> str:
        return f"<Task {self.id!r} {self.status.value!r}>"


# ---------------------------------------------------------------------------
# Report — analysis output (1:1 with Task)
# ---------------------------------------------------------------------------

class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_new_id)

    task_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    markdown_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    structured_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    metric_cards: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    quality_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)

    citations_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    token_usage: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    task: Mapped[Task] = relationship(back_populates="report")

    def __repr__(self) -> str:
        return f"<Report task={self.task_id!r}>"


# ---------------------------------------------------------------------------
# ExecutionLog — per-agent trace event
# ---------------------------------------------------------------------------

class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    task_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    agent_name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="planner | research | analysis | writer | reviewer"
    )
    event_type: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="started | completed | error | progress"
    )
    data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    task: Mapped[Task] = relationship(back_populates="execution_logs")

    __table_args__ = (
        # Composite index for the most common query pattern
        {"comment": "Per-agent execution trace for observability and timeline replay"},
    )

    def __repr__(self) -> str:
        return f"<ExecutionLog task={self.task_id!r} agent={self.agent_name!r} {self.event_type!r}>"
