import httpx
from langchain_core.tools import tool

from backend.config import settings


@tool
async def tavily_search(query: str, max_results: int = 5) -> list[dict]:
    """Search the web using Tavily Search API."""
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
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
        return [{"url": r["url"], "title": r["title"], "content": r["content"]} for r in data.get("results", [])]


@tool
async def firecrawl_extract(url: str) -> dict:
    """Extract structured content from a URL using Firecrawl."""
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            "https://api.firecrawl.dev/v1/scrape",
            json={"url": url},
            headers={"Authorization": f"Bearer {settings.FIRECRAWL_API_KEY}"},
        )
        resp.raise_for_status()
        return resp.json()
