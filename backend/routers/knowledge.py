"""
FastAPI Router for Tenant Knowledge Ingestion & Qdrant Semantic Search.
Allows any business tenant to upload FAQs, documents, policies, and service menus.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from core.engine.qdrant_rag import qdrant_engine
from core.blueprint.tenant_manager import tenant_registry

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge Ingestion & Vector RAG"])


class IngestChunkRequest(BaseModel):
    tenant_id: str
    text: str
    category: Optional[str] = "general"
    title: Optional[str] = "Manual Ingestion"
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class KnowledgeQueryRequest(BaseModel):
    tenant_id: str
    query: str
    top_k: Optional[int] = 3


@router.post("/ingest")
def ingest_tenant_document(payload: IngestChunkRequest):
    """
    Ingests text into the specified tenant's isolated vector partition.
    Guarantees isolation between business tenants.
    """
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text payload cannot be empty")

    meta = payload.metadata or {}
    meta["title"] = payload.title

    result = qdrant_engine.ingest_document(
        tenant_id=payload.tenant_id,
        text=payload.text.strip(),
        category=payload.category or "general",
        metadata=meta
    )

    return {
        "status": "success",
        "message": f"Successfully indexed knowledge chunk into partition '{payload.tenant_id}'",
        "details": result
    }


@router.post("/query")
def query_tenant_knowledge(payload: KnowledgeQueryRequest):
    """
    Performs semantic vector search against a single tenant's partition.
    """
    res = qdrant_engine.retrieve(
        tenant_id=payload.tenant_id,
        query=payload.query,
        top_k=payload.top_k or 3
    )
    return res


@router.get("/stats")
def get_tenant_knowledge_stats(tenant_id: str = Query("salon")):
    """Returns indexed knowledge chunks for a given tenant."""
    clean_tenant = tenant_id.strip().lower()
    local_chunks = qdrant_engine._local_points.get(clean_tenant, [])
    return {
        "tenant_id": clean_tenant,
        "indexed_chunks_count": len(local_chunks),
        "qdrant_connected": qdrant_engine.connected_to_cloud,
        "semantic_cache_entries": len([k for k in qdrant_engine._semantic_cache if k.startswith(f"{clean_tenant}::")])
    }

