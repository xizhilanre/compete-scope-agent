"""
ToolRouter — central registry for agent-callable tools.

Provides a single entry point (``call_sync``) that dispatches by tool
name, measures execution time, and records a call log for observability.
"""

import time
from typing import Any

from backend.tools.tavily_search import tavily_search_sync


class ToolRouter:
    """Synchronous tool dispatcher with built-in call logging.

    Usage::

        router = ToolRouter(task_id="abc123")
        result = router.call_sync("tavily_search", query="...")
        print(router.get_call_log())
    """

    def __init__(self, task_id: str) -> None:
        self._task_id = task_id
        self._call_log: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def call_sync(self, tool_name: str, **kwargs: Any) -> Any:
        """Dispatch *tool_name* with *kwargs* and return its result.

        Raises ``ValueError`` for unknown tool names.  On exception the
        error is recorded in the call log and then re-raised.
        """
        start = time.time()
        ok = True
        error: str | None = None

        try:
            result = self._dispatch(tool_name, **kwargs)
            return result
        except Exception as exc:
            ok = False
            error = str(exc)
            raise
        finally:
            elapsed_ms = round((time.time() - start) * 1000, 2)
            self._call_log.append(
                {
                    "tool": tool_name,
                    "duration_ms": elapsed_ms,
                    "ok": ok,
                    "error": error,
                }
            )

    def get_call_log(self) -> list[dict[str, Any]]:
        """Return the accumulated call log."""
        return list(self._call_log)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _dispatch(self, tool_name: str, **kwargs: Any) -> Any:
        if tool_name == "tavily_search":
            return tavily_search_sync(**kwargs)

        msg = f"Unknown tool: {tool_name!r}"
        raise ValueError(msg)
