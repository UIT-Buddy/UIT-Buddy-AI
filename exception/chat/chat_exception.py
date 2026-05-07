"""ChatException for chat flow failures with explicit HTTP status codes."""

from __future__ import annotations

from exception.chat.chat_error_code import ChatErrorDefinition


class ChatException(Exception):
    """Raised for chat-specific errors that should be exposed via API."""

    def __init__(self, status_code: int, message: str, error_code: str = "CHAT_ERROR"):
        self.status_code = status_code
        self.message = message
        self.error_code = error_code
        super().__init__(f"[{status_code}] {error_code}: {message}")

    @classmethod
    def from_definition(
        cls,
        error: ChatErrorDefinition,
        message: str | None = None,
    ) -> "ChatException":
        return cls(
            status_code=error.status_code,
            message=message or error.message,
            error_code=error.code,
        )
