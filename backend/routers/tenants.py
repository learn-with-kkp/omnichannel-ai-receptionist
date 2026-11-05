"""
Tenants & Universal Blueprint API Router.
Enables instant plug-and-play vertical switching across:
- Salon & Spa
- Dental Health Clinic
- Automotive Repair & Tires
- Family Medical Clinic
And multi-accent English pronunciation configuration.
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from core.blueprint.tenant_manager import tenant_registry
from core.blueprint.schema import BusinessProfile, AccentProfile
from core.engine.rag_engine import knowledge_engine
from integrations.google_calendar import calendar_service

logger = logging.getLogger("TenantsRouter")
router = APIRouter(prefix="/api/blueprint", tags=["Blueprint"])


class RagToggleRequest(BaseModel):
    enabled: bool


@router.get("/status")
def get_blueprint_status():
    """System health, Google Calendar sync status, RAG mode, and tenant count."""
    return {
        "status": "operational",
        "google_calendar_connected": calendar_service.is_connected() if calendar_service else False,
        "rag_mode_enabled": knowledge_engine.use_rag,
        "available_verticals": [t.id for t in tenant_registry.list_tenants()],
        "available_accents": [a.key for a in tenant_registry.list_accents()]
    }


@router.get("/tenants")
def list_blueprint_tenants():
    """Returns all ready-to-sell vertical industry manifests."""
    tenants = tenant_registry.list_tenants()
    return {
        "tenants": [
            {
                "id": t.id,
                "name": t.name,
                "industry": t.industry,
                "phone": t.phone,
                "address": t.address,
                "services_count": len(t.services),
                "staff_count": len(t.staff),
                "currency": t.currency,
                "lead_time_hours": t.business_rules.min_lead_time_hours,
                "cancellation_window_hours": t.business_rules.cancellation_window_hours
            }
            for t in tenants
        ]
    }


@router.get("/tenants/{tenant_id}")
def get_tenant_details(tenant_id: str):
    """Retrieves full manifest for a specific industry tenant."""
    tenant = tenant_registry.get_tenant(tenant_id)
    return {"tenant": tenant.model_dump()}


@router.get("/accents")
def list_accent_profiles():
    """Returns available English pronunciation / accent profiles."""
    accents = tenant_registry.list_accents()
    return {
        "accents": [a.model_dump() for a in accents]
    }


@router.post("/set-rag")
def toggle_rag_mode(payload: RagToggleRequest):
    """Toggle between RAG (vector retrieval) and RAGless (unified context) modes."""
    knowledge_engine.set_rag_mode(payload.enabled)
    mode_str = "RAG (Vector Cosine Retrieval)" if payload.enabled else "RAGless (Direct Prompt Assembly)"
    logger.info(f"Knowledge Retrieval Mode switched to: {mode_str}")
    return {"status": "success", "rag_mode": payload.enabled, "mode_description": mode_str}
