"""Authentication status values used in backend context payload."""

from __future__ import annotations

from enum import Enum


class AuthStatus(str, Enum):
    OK = "ok"
    MISSING_OR_INVALID = "missing_or_invalid"
