"""Unified API response envelope — every endpoint wraps its payload in this."""

from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Envelope[T](BaseModel):
    """Standard API response wrapper.

    All endpoints return:
        {"success": true, "data": <payload>, "error": null}
    """

    success: bool = True
    data: T | None = None
    error: str | None = None

    model_config = {"from_attributes": True}


def ok[T](data: T) -> Envelope[T]:
    """Shorthand for a successful response."""
    return Envelope(success=True, data=data, error=None)


def err(message: str) -> Envelope[None]:
    """Shorthand for an error response."""
    return Envelope(success=False, data=None, error=message)
