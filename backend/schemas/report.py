"""Report schemas — nested SWOT, MetricCards, citations."""

from datetime import datetime

from pydantic import BaseModel
from pydantic import Field

# ---------------------------------------------------------------------------
# Nested models
# ---------------------------------------------------------------------------

class SWOTItem(BaseModel):
    category: str = Field(..., examples=["strength"])
    point: str = Field(..., examples=["Market leader in collaborative document editing"])
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    citations: list[str] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class MetricCard(BaseModel):
    label: str = Field(..., examples=["Pricing (USD/month)"])
    value: str = Field(..., examples=["$10-$25"])
    trend: str | None = Field(default=None, examples=["up"])
    competitor_count: int = Field(default=0)

    model_config = {"from_attributes": True}


class CitationEntry(BaseModel):
    url: str
    title: str
    snippet: str
    retrieved_at: datetime | None = None

    model_config = {"from_attributes": True}


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_estimate_usd: float = 0.0

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------

class ReportResponse(BaseModel):
    id: str
    task_id: str
    task_target_product: str = Field(default="", description="Denormalised for convenience")
    markdown_content: str | None = None
    structured_data: dict | None = None
    swot: list[SWOTItem] = Field(default_factory=list)
    metric_cards: list[MetricCard] = Field(default_factory=list)
    citations: list[CitationEntry] = Field(default_factory=list)
    token_usage: TokenUsage | None = None
    quality_score: float | None = None
    quality_feedback: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
