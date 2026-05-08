"""Configuration for LightRAG + Neo4j + Claude + SiliconCloud.

Only two providers are used:
  • LLM      — Claude  (via shopaikey.com)
  • Embedding — SiliconCloud (BAAI/bge-m3, OpenAI-compatible)
"""

from __future__ import annotations
import os
from dotenv import load_dotenv

load_dotenv()


NEO4J_URI: str = os.getenv("NEO4J_URI")
NEO4J_USERNAME: str = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD")

CLAUDE_API_KEY: str = os.getenv("CLAUDE_API_KEY")
CLAUDE_BASE_URL: str = os.getenv("CLAUDE_BASE_URL")
CLAUDE_MODEL_NAME: str = os.getenv("CLAUDE_MODEL_NAME")

SILICONCLOUD_API_KEY: str = os.getenv("SILICONCLOUD_API_KEY")
SILICONCLOUD_BASE_URL: str = os.getenv("SILICONCLOUD_BASE_URL")
SILICONCLOUD_EMBEDDING_MODEL: str = os.getenv("SILICONCLOUD_EMBEDDING_MODEL")


RAG_WORKING_DIR: str = os.getenv("RAG_WORKING_DIR", "./rag_working")
CHUNK_TOKEN_SIZE: int = int(os.getenv("CHUNK_TOKEN_SIZE", "1024"))
CHUNK_OVERLAP_TOKEN_SIZE: int = int(os.getenv("CHUNK_OVERLAP_TOKEN_SIZE", "100"))
