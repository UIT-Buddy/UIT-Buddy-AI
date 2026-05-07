"""Chat service error definitions (status_code, code, message)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChatErrorDefinition:
    status_code: int
    code: str
    message: str


class ChatErrorCode:
    AUTH_REQUIRED = ChatErrorDefinition(
        status_code=401,
        code="CHAT_AUTH_REQUIRED",
        message="Authentication token is required for lookup questions.",
    )
    BACKEND_UNAVAILABLE = ChatErrorDefinition(
        status_code=502,
        code="CHAT_BACKEND_UNAVAILABLE",
        message="Failed to retrieve user-specific data from backend.",
    )
    LLM_CLASSIFICATION_FAILED = ChatErrorDefinition(
        status_code=500,
        code="CHAT_CLASSIFICATION_FAILED",
        message="Failed to classify chat question.",
    )
    PROCESSING_ERROR = ChatErrorDefinition(
        status_code=500,
        code="CHAT_PROCESSING_ERROR",
        message="Unexpected chat processing error.",
    )
