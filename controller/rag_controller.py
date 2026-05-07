"""controller/rag_controller.py — FastAPI router for /api/rag/*.

No business logic here — only HTTP handling.
Business logic lives in service/rag/rag_service.py.
"""

from __future__ import annotations
from service.rag import get_rag_service

from fastapi import APIRouter, HTTPException, File, UploadFile

router = APIRouter(prefix="/api/rag", tags=["rag"])


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)) -> dict:
    """Upload a document (PDF, DOCX, etc.) to index into LightRAG."""
    content = await file.read()
    return await get_rag_service().index_file(content, file.filename)


@router.get("/files")
async def list_documents() -> dict:
    """List all documents indexed in LightRAG."""
    return await get_rag_service().list_uploads()
