"""rag/rag.py — LightRAG engine with Neo4j (graph) + NanoVectorDB (vector).

Mirrors how backend/ wraps HTTP calls. Here we wrap LightRAG operations.

Storage plan:
  • chunk_entity_relation_graph  → Neo4JStorage  (entity nodes + relationships)
  • entities_vdb                 → NanoVectorDBStorage  (entity embeddings)
  • relationships_vdb             → NanoVectorDBStorage  (relationship embeddings)
  • chunks_vdb                   → NanoVectorDBStorage  (chunk embeddings)
  • full_docs / text_chunks      → JsonKVStorage  (raw text, lives in rag_working/)
  • llm_response_cache           → JsonKVStorage
  • doc_status                   → JsonDocStatusStorage
"""

from __future__ import annotations

import os
from lightrag.lightrag import LightRAG, QueryParam

from config.rag_config import (
    RAG_WORKING_DIR,
    CHUNK_TOKEN_SIZE,
    CHUNK_OVERLAP_TOKEN_SIZE,
)
from client.rag_client import get_llm_func, get_embedding_func

_rag: LightRAG | None = None
_rag_initialized: bool = False


def get_rag() -> LightRAG:
    """Get or create the shared LightRAG instance (singleton).
    Note: Storages must be initialized via initialize_storages() before use.
    """
    global _rag
    if _rag is not None:
        return _rag

    working_dir = RAG_WORKING_DIR
    os.makedirs(working_dir, exist_ok=True)
    _rag = LightRAG(
        working_dir=working_dir,
        llm_model_func=get_llm_func(),
        embedding_func=get_embedding_func(),
        vector_storage="NanoVectorDBStorage",
        kv_storage="JsonKVStorage",
        graph_storage="Neo4JStorage",
        chunk_token_size=CHUNK_TOKEN_SIZE,
        chunk_overlap_token_size=CHUNK_OVERLAP_TOKEN_SIZE,
        llm_model_max_async=16,
        max_total_tokens=32768,
    )
    return _rag


async def get_initialized_rag() -> LightRAG:
    """Get the RAG instance and ensure its storages are initialized."""
    global _rag_initialized
    rag = get_rag()
    if not _rag_initialized:
        await rag.initialize_storages()
        _rag_initialized = True
    return rag


async def query(
    question: str,
    mode: str = "mix",
    top_k: int = 10,
    response_type: str = "Multiple Paragraphs",
    only_need_context: bool = False,
    major_anchor: str | None = None,
) -> str:
    """Query LightRAG and return the generated answer (string).

    Returns an empty string on error so callers always get a valid string.
    """
    rag = await get_initialized_rag()
    param = QueryParam(
        mode=mode,
        top_k=top_k,
        response_type=response_type,
        only_need_context=only_need_context,
    )
    # Enrich the question with UIT hierarchy logic and major anchor to guide the graph retrieval
    anchor_info = f"Major Anchor: {major_anchor}. " if major_anchor else ""
    enriched_question = (
        f"{anchor_info}Search Guidance: UIT subject types include ĐC (General), CSN (Foundation), "
        f"CT (Political), CN (Major), and CNTC (Major Electives). "
        f"Prerequisite flow: ĐC -> CSN/CT -> CN -> CNTC. "
        f"Question: {question}"
    )
    try:
        result = await rag.aquery(enriched_question, param=param)
        if hasattr(result, "__anext__"):
            parts: list[str] = []
            async for chunk in result:
                parts.append(str(chunk))
            return "".join(parts)
        return str(result) if result is not None else ""
    except Exception as e:
        print(f"[LightRAG query error] {e}")
        return ""


async def query_context(
    question: str,
    mode: str = "hybrid",
    top_k: int = 60,
    major_anchor: str | None = None,
) -> str:
    """Query LightRAG but return ONLY the retrieved context, no LLM generation."""
    rag = await get_initialized_rag()
    param = QueryParam(
        mode=mode,
        top_k=top_k,
        only_need_context=True,
    )
    # Enrich the question with UIT hierarchy logic and major anchor for better context extraction
    anchor_info = f"Major Anchor: {major_anchor}. " if major_anchor else ""
    enriched_question = (
        f"{anchor_info}Search Guidance: UIT subject types include ĐC (General), CSN (Foundation), "
        f"CT (Political), CN (Major), and CNTC (Major Electives). "
        f"Prerequisite flow: ĐC -> CSN/CT -> CN -> CNTC. "
        f"Question: {question}"
    )
    try:
        result = await rag.aquery(enriched_question, param=param)
        if hasattr(result, "__anext__"):
            parts: list[str] = []
            async for chunk in result:
                parts.append(str(chunk))
            return "".join(parts)
        return str(result) if result is not None else ""
    except Exception as e:
        print(f"[LightRAG query_context error] {e}")
        return ""


async def index_documents(texts: list[str]) -> list[str]:
    """Index a list of raw text documents. Returns list of doc IDs."""
    rag = await get_initialized_rag()
    doc_ids = []
    for text in texts:
        doc_id = await rag.ainsert(text)
        doc_ids.append(str(doc_id))
    return doc_ids


async def index_file(text: str) -> str:
    """Index a single document (already converted to text). Returns doc ID."""
    rag = await get_initialized_rag()
    doc_id = await rag.ainsert(text)
    return str(doc_id)


async def delete_document(doc_id: str) -> dict:
    """Delete a document and all its data from LightRAG."""
    rag = await get_initialized_rag()
    await rag.adelete_by_doc_id(doc_id)
    return {"deleted": doc_id}


async def get_document_status(doc_id: str) -> dict:
    """Get processing status of a document."""
    rag = await get_initialized_rag()
    return await rag.get_doc_status(doc_id)
