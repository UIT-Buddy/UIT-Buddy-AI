"""rag/__init__.py — re-export the public API."""

from rag.rag import (
    get_rag,
    query,
    query_context,
    index_documents,
    index_file,
    delete_document,
    get_document_status,
)

__all__ = [
    "get_rag",
    "query",
    "query_context",
    "index_documents",
    "index_file",
    "delete_document",
    "get_document_status",
]
