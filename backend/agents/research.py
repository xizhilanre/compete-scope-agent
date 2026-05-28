"""
Research Agent -- executes the search queries produced by the Planner and
collects raw research results.  In mock mode it returns hardcoded snippets;
in real mode it delegates to ``ToolRouter`` (which wraps the Tavily API).
"""

import asyncio

from backend.api.routes.events import publish
from backend.core.state import AnalysisState
from backend.schemas.events import AgentStartEvent, AgentCompleteEvent, iso_now
from backend.tools.registry import ToolRouter

MOCK_RESEARCH = [
    {
        "title": "{product} — Best-in-class collaborative workspace",
        "url": "https://example.com/review-1",
        "content": (
            "{product} dominates the collaborative workspace market with over"
            " 100M users. Key features include real-time editing, database"
            " views, and integrations."
        ),
        "relevance_score": 0.95,
    },
    {
        "title": "{product} Pricing & Plans 2026",
        "url": "https://example.com/pricing-1",
        "content": (
            "Free tier available. Plus plan at $10/user/month. Business plan"
            " at $18/user/month. Enterprise custom pricing."
        ),
        "relevance_score": 0.88,
    },
    {
        "title": "Top {product} Competitors & Alternatives",
        "url": "https://example.com/competitors-1",
        "content": (
            "Main competitors include Coda, Confluence, and ClickUp."
            " {product} leads in user experience and integrations."
        ),
        "relevance_score": 0.82,
    },
]


async def run_research(state: AnalysisState, mock: bool = True) -> dict:
    task_id = state["task_id"]
    product = state["target_product"]

    await publish(
        task_id,
        AgentStartEvent(task_id=task_id, agent="research", timestamp=iso_now()),
    )

    if mock:
        await asyncio.sleep(2)
        results = []
        for item in MOCK_RESEARCH:
            r = dict(item)
            r["title"] = r["title"].format(product=product)
            r["content"] = r["content"].format(product=product)
            results.append(r)
    else:
        router = ToolRouter(task_id)
        results = []
        seen_urls: set[str] = set()
        for query in state["search_queries"]:
            try:
                batch = router.call_sync("tavily_search", query=query, max_results=3)
                for item in batch:
                    if item["url"] not in seen_urls:
                        seen_urls.add(item["url"])
                        results.append(item)
            except Exception:
                continue

    await publish(
        task_id,
        AgentCompleteEvent(
            task_id=task_id,
            agent="research",
            timestamp=iso_now(),
            duration_ms=2000,
            output_summary=f"收集了 {len(results)} 条搜索结果",
        ),
    )

    return {
        "raw_research": results,
        "current_agent": "research",
    }
