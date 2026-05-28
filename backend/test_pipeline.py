"""
CLI end-to-end test for the CompeteScope DAG pipeline.

Usage:
    PYTHONPATH=. python backend/test_pipeline.py "Notion"
    PYTHONPATH=. python backend/test_pipeline.py "Figma"
"""

import asyncio
import sys

from backend.core.runtime import run_dag


async def main() -> None:
    product = sys.argv[1] if len(sys.argv) > 1 else "Notion"
    task_id = "test-" + product.lower().replace(" ", "-")
    print(f"Starting analysis for: {product} (task_id={task_id})")
    await run_dag(task_id, product, ["功能分析", "定价策略", "SWOT分析", "市场定位"])
    print(f"Done! Check database for task_id={task_id}")


if __name__ == "__main__":
    asyncio.run(main())
