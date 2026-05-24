"""Report routes — read generated competitive analysis reports.

MOCK DATA — replace with real DB queries after wiring up the repository layer.
"""

from datetime import UTC
from datetime import datetime

from fastapi import APIRouter

from backend.schemas.base import Envelope
from backend.schemas.base import err
from backend.schemas.base import ok
from backend.schemas.report import CitationEntry
from backend.schemas.report import MetricCard
from backend.schemas.report import ReportResponse
from backend.schemas.report import SWOTItem
from backend.schemas.report import TokenUsage

router = APIRouter(tags=["reports"], prefix="/reports")

# ---------------------------------------------------------------------------
# Mock data
# ---------------------------------------------------------------------------

_MOCK_REPORT = ReportResponse(
    id="r1p2o3r4t5",
    task_id="a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6",
    task_target_product="Notion",
    markdown_content=(
        "# Competitive Analysis: Notion\n\n"
        "## Executive Summary\n"
        "Notion dominates the all-in-one workspace category...\n\n"
        "## SWOT Analysis\n"
        "See structured data below.\n"
    ),
    structured_data={
        "competitors": ["Coda", "Confluence", "Craft", "Obsidian"],
        "market_segments": ["SMB", "Enterprise", "Personal"],
    },
    swot=[
        SWOTItem(
            category="strength",
            point="Market leader in collaborative document editing",
            confidence=0.94,
            citations=["https://example.com/notion-growth-2026"],
        ),
        SWOTItem(
            category="strength",
            point="Strong third-party integrations ecosystem",
            confidence=0.88,
            citations=["https://example.com/notion-integrations"],
        ),
        SWOTItem(
            category="weakness",
            point="Performance degrades with large workspaces",
            confidence=0.78,
            citations=["https://example.com/notion-perf"],
        ),
        SWOTItem(
            category="opportunity",
            point="AI-native features driving enterprise adoption",
            confidence=0.91,
            citations=["https://example.com/notion-ai"],
        ),
        SWOTItem(
            category="threat",
            point="Coda gaining traction with dev-focused teams",
            confidence=0.72,
            citations=["https://example.com/coda-vs-notion"],
        ),
    ],
    metric_cards=[
        MetricCard(label="Pricing (USD/month)", value="$0-$18", trend="stable", competitor_count=8),
        MetricCard(label="G2 Rating", value="4.7 / 5", trend="up", competitor_count=12),
        MetricCard(label="Web Traffic (est.)", value="~120M/mo", trend="up", competitor_count=6),
    ],
    citations=[
        CitationEntry(
            url="https://example.com/notion-growth-2026",
            title="Notion Crosses 100M Users in 2026",
            snippet="Notion has surpassed 100 million users...",
            retrieved_at=datetime(2026, 5, 24, 10, 1, 30, tzinfo=UTC),
        ),
        CitationEntry(
            url="https://example.com/notion-ai",
            title="How Notion AI Is Changing Enterprise Productivity",
            snippet="Notion AI features have driven a 40 % increase...",
            retrieved_at=datetime(2026, 5, 24, 10, 2, 15, tzinfo=UTC),
        ),
    ],
    token_usage=TokenUsage(
        prompt_tokens=12400,
        completion_tokens=3800,
        total_tokens=16200,
        cost_estimate_usd=0.34,
    ),
    quality_score=0.87,
    quality_feedback="Good coverage. Consider adding pricing-tier breakdown per competitor.",
    created_at=datetime(2026, 5, 24, 10, 9, 30, tzinfo=UTC),
)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/{report_id}", response_model=Envelope[ReportResponse])
async def get_report(report_id: str) -> Envelope[ReportResponse]:
    """Get a structured analysis report by ID."""
    if report_id == _MOCK_REPORT.id:
        return ok(_MOCK_REPORT)
    return err(f"Report {report_id!r} not found")
