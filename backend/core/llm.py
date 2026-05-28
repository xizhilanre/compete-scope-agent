"""
LLM invocation utilities for CompeteScope agents.

Two helpers:

* ``get_llm`` — builds a langchain ``ChatOpenAI`` instance from
  ``backend.config.settings`` (API key, base URL, model name).

* ``safe_parse_json`` — extracts a JSON dict from raw LLM text output,
  trying three strategies in order of safety.
"""

import json
import re
from typing import Any

from langchain_openai import ChatOpenAI

from backend.config import settings


def get_llm(
    temperature: float = 0.3,
    max_tokens: int = 3000,
) -> ChatOpenAI:
    """Return a configured ChatOpenAI instance.

    Reads model / api_key / base_url from ``backend.config.settings``.
    ``base_url`` is only forwarded when it is set (not None / not empty).
    """
    kwargs: dict[str, Any] = {
        "model": settings.OPENAI_MODEL,
        "api_key": settings.OPENAI_API_KEY,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "timeout": 90,
    }
    if settings.OPENAI_BASE_URL:
        kwargs["base_url"] = settings.OPENAI_BASE_URL

    return ChatOpenAI(**kwargs)


def safe_parse_json(raw: str) -> dict[str, Any]:
    """Safely extract a JSON dict from *raw* LLM output.

    Strategies tried in order:
        1. Direct ``json.loads``.
        2. Regex for `` ```json … ``` `` code blocks.
        3. Find the first ``{`` and last ``}`` in the string and parse
           that substring.
        4. Return ``{}`` when all of the above fail.
    """
    # Strategy 1 — direct parse
    raw_stripped = raw.strip()
    if raw_stripped:
        try:
            return json.loads(raw_stripped)
        except json.JSONDecodeError:
            pass

    # Strategy 2 — ```json … ``` code block
    m = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", raw, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Strategy 3 — first { to last }
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(raw[start : end + 1])
        except json.JSONDecodeError:
            pass

    # Strategy 4 — give up
    return {}
