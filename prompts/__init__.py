"""prompts/ — Centralised prompt strings for BuddyAI.

Re-exports:
    CHAT_ANSWER_SYSTEM — system prompt for final grounded answer generation.
    CHAT_ANSWER_USER_TEMPLATE — user template that injects backend + RAG context.
    BACKEND_ENDPOINT_PLANNER_SYSTEM — system prompt for backend endpoint planning.
    BACKEND_ENDPOINT_PLANNER_USER_TEMPLATE — user template for backend endpoint planning.
    CHAT_ENDPOINT_CONTRACT — instruction prompt for external AI chat endpoint usage.
"""

from prompts.chat_answer import CHAT_ANSWER_SYSTEM, CHAT_ANSWER_USER_TEMPLATE
from prompts.backend_planner import (
    BACKEND_ENDPOINT_PLANNER_SYSTEM,
    BACKEND_ENDPOINT_PLANNER_USER_TEMPLATE,
)
from prompts.chat_endpoint_contract import CHAT_ENDPOINT_CONTRACT

__all__ = [
    "CHAT_ANSWER_SYSTEM",
    "CHAT_ANSWER_USER_TEMPLATE",
    "BACKEND_ENDPOINT_PLANNER_SYSTEM",
    "BACKEND_ENDPOINT_PLANNER_USER_TEMPLATE",
    "CHAT_ENDPOINT_CONTRACT",
]
