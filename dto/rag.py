"""dto/rag.py — FastAPI request/response models for RAG endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str
    authentication: str = Field(
        description="Bearer token or raw JWT for authentication"
    )


class ChatResponse(BaseModel):
    answer: str
