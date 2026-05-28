"""
Synchronous Tavily Search wrapper.

Provides a single function ``tavily_search_sync`` that POSTs to the
Tavily Search API via ``httpx`` and returns a normalised list of result
dicts.
"""

from typing import Any

import httpx

from backend.config import settings


def tavily_search_sync(
    query: str,
    max_results: int = 5,
) -> list[dict[str, Any]]:
    """Execute a synchronous Tavily web search.

    Args:
        query: Search query string.
        max_results: Number of results to return (default 5).

    Returns:
        List of dicts with keys ``title``, ``url``, ``content``,
        ``relevance_score``.

    Raises:
        httpx.HTTPStatusError: On non-2xx response from the API.
    """
    with httpx.Client(timeout=30) as client:
        resp = client.post(
            "https://api.tavily.com/search",
            json={
                "api_key": settings.TAVILY_API_KEY,
                "query": query,
                "max_results": max_results,
                "search_depth": "advanced",
            },
        )
        resp.raise_for_status()
        data = resp.json()

    results: list[dict[str, Any]] = []
    for r in data.get("results", []):
        content = (r.get("content") or "")[:300]
        results.append(
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": content,
                "relevance_score": float(r.get("score", 0.0)),
            }
        )
    return results
