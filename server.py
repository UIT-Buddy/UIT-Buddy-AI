"""FastAPI server — exposes UIT Buddy Backend APIs to BuddyAI."""

from __future__ import annotations
from fastapi.responses import RedirectResponse

from typing import Annotated

from fastapi import FastAPI, Header, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from config.app_config import SERVER_PORT
from service.backend.buddy_service import get_buddy_service
from client.buddy_client import UITBuddyClient
from exception.buddy.buddy_exception import BackendAPIError

from controller.chat_controller import router as chat_router
from controller.rag_controller import router as rag_router

app = FastAPI(
    title="BuddyAI — UIT Buddy Backend Proxy + RAG",
    description="Proxies authenticated requests to UIT Buddy Backend and provides academic RAG.",
)

app.include_router(chat_router)
app.include_router(rag_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    client = UITBuddyClient()
    response = await client.get(path="/docs", token=None, params=None)
    if response is None:
        return {"status": "error", "detail": "Cannot reach UIT Buddy Backend"}
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=SERVER_PORT)
