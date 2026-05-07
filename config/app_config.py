"""Configuration for the UIT Buddy Backend client."""

from __future__ import annotations
from dotenv import load_dotenv
import os

load_dotenv()

_base = os.getenv("UIT_BUDDY_BASE_URL")
if _base:
    _base = _base.rstrip("/")

_port = os.getenv("UIT_BUDDY_BACKEND_PORT", "")
UIT_BUDDY_BASE_URL: str = f"{_base}:{_port}" if _port else _base
UIT_BUDDY_WEBHOOK_URL: str = _base

UIT_BUDDY_TIMEOUT: int = int(os.getenv("UIT_BUDDY_TIMEOUT", "30"))

SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))




