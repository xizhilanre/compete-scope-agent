"""
AnalysisState — shared data bus for the 5-agent LangGraph pipeline.

Every agent node reads from and writes to this TypedDict as it passes
through the DAG.  Fields are grouped by producer agent.
"""

from typing import Annotated, Optional, TypedDict
import operator


class AnalysisState(TypedDict):
    # ---- 输入 ----
    task_id: str
    target_product: str
    analysis_dimensions: list[str]

    # ---- Planner 输出 ----
    search_queries: list[str]
    analysis_plan: str

    # ---- Research 输出 ----
    raw_research: list[dict]

    # ---- Analysis 输出 ----
    structured_analysis: Optional[dict]

    # ---- Writer 输出 ----
    final_report_markdown: str
    metric_cards: Optional[dict]

    # ---- Reviewer 输出 ----
    quality_score: float
    quality_feedback: str

    # ---- Runtime 跟踪 ----
    current_agent: str
    execution_logs: Annotated[list[dict], operator.add]
    token_usage: dict
    llm_call_count: int
    status: str
    error: Optional[str]
