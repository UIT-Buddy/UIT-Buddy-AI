"""Buddy service error definitions (status_code, code, message)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BuddyErrorDefinition:
    status_code: int
    code: str
    message: str


class BuddyErrorCode:
    MISSING_TOKEN = BuddyErrorDefinition(
        status_code=401,
        code="BUDDY_AUTH_REQUIRED",
        message="Authorization token is required.",
    )
    INVALID_TOKEN = BuddyErrorDefinition(
        status_code=401,
        code="BUDDY_AUTH_INVALID",
        message="Authorization token is invalid.",
    )
    BACKEND_TIMEOUT = BuddyErrorDefinition(
        status_code=504,
        code="BUDDY_BACKEND_TIMEOUT",
        message="Buddy backend request timed out.",
    )
    BACKEND_UNAVAILABLE = BuddyErrorDefinition(
        status_code=502,
        code="BUDDY_BACKEND_UNAVAILABLE",
        message="Buddy backend is unavailable.",
    )
    UNKNOWN_ERROR = BuddyErrorDefinition(
        status_code=500,
        code="BUDDY_UNKNOWN_ERROR",
        message="Unexpected buddy service error.",
    )
