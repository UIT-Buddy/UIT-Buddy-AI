"""controller/chat_controller.py — FastAPI router for /api/chat.

No business logic here — only HTTP handling.
Business logic lives in service/rag/rag_service.py.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from dto import ChatRequest, ChatResponse
from service.rag import get_rag_service
from exception.chat.chat_exception import ChatException

def _clean_auth_token(token: str | None) -> str | None:
    """Remove a leading “Bearer ” from the token if present."""
    if token is None:
        return None
    token = token.strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    print("token", token)
    return token

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint.
    Every question is answered via RAG context + backend data + LLM.
    """
    # Clean the token before handing it to the service layer
    request.authentication = _clean_auth_token(request.authentication)
    service = get_rag_service()
    try:
        return await service.chat(request)
    except ChatException as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={"code": exc.error_code, "message": exc.message},
        )
