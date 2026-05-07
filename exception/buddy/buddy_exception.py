from __future__ import annotations

from exception.buddy.buddy_error_code import BuddyErrorDefinition


class BackendAPIError(Exception):
    """Raised when the UIT Buddy Backend returns a non-2xx response."""

    def __init__(
        self, status_code: int, detail: str, code: str = "BUDDY_BACKEND_ERROR"
    ):
        self.status_code = status_code
        self.detail = detail
        self.code = code
        super().__init__(f"[{status_code}] {code}: {detail}")

    @classmethod
    def from_definition(
        cls,
        error: BuddyErrorDefinition,
        detail: str | None = None,
    ) -> "BackendAPIError":
        return cls(
            status_code=error.status_code,
            detail=detail or error.message,
            code=error.code,
        )
