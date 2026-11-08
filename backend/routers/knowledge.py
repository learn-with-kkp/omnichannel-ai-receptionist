"""
FastAPI Router for Tenant Knowledge Ingestion & Semantic Search.
Allows any business tenant to upload FAQs, documents, policies, and service menus.
"""

import io
import logging
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from pypdf import PdfReader
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from core.engine.qdrant_rag import qdrant_engine
from core.blueprint.tenant_manager import tenant_registry

logger = logging.getLogger("KnowledgeRouter")
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


@router.post("/upload-pdf")
async def upload_salon_pdf_document(
    file: UploadFile = File(...),
    tenant_id: str = Form("salon"),
    category: str = Form("salon_menu_and_policies")
):
    """
    Extracts text content from uploaded Salon Menu, Services Catalog, or Policy PDF
    and indexes it into vector knowledge memory.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    
    try:
        reader = PdfReader(io.BytesIO(contents))
        extracted_pages = []
        for idx, page in enumerate(reader.pages):
            text = (page.extract_text() or "").strip()
            if text:
                extracted_pages.append(f"[Page {idx + 1}]\n{text}")
        
        full_text = "\n\n".join(extracted_pages)
        if not full_text:
            raise HTTPException(status_code=400, detail="No extractable text found in PDF.")
        
        result = qdrant_engine.ingest_document(
            tenant_id=tenant_id.strip().lower(),
            text=full_text,
            category=category,
            metadata={
                "filename": file.filename,
                "total_pages": len(reader.pages),
                "source": "website_pdf_upload"
            }
        )
        return {
            "status": "success",
            "message": f"Successfully ingested {file.filename} ({len(reader.pages)} pages) into Luxe Salon vector knowledge base!",
            "details": result,
            "snippet": full_text[:300] + "..."
        }
    except Exception as e:
        logger.error(f"Error parsing PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

