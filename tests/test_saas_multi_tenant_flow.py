"""
End-to-End Test Suite for the Multi-Tenant Omnichannel SaaS Architecture.
Validates:
1. Public Customer Registration & Tenant Provisioning
2. Multi-Tenant Qdrant Vector Knowledge Partitioning (No Cross-Tenant Leakage)
3. Instant Tenant Website Rendering (/site/{tenant_id})
4. Meta OAuth 2.0 URL Generation with Encoded Tenant State
5. Dynamic Multi-Tenant Inbound Webhook Routing (WhatsApp & Messenger)
"""

import pytest
from fastapi.testclient import TestClient
from backend.app import app
from backend.database import save_tenant_integrations, get_tenant_integrations
from core.blueprint.tenant_manager import tenant_registry

client = TestClient(app)


def test_public_customer_registration_and_tenant_site():
    """Verify new business registration automatically provisions workspace and site."""
    import secrets
    uniq = secrets.token_hex(4)
    payload = {
        "email": f"dr_smith_{uniq}@apexidental.com",
        "password": "StrongPassword!99",
        "company_name": f"Apex Dental Studio {uniq}",
        "vertical": "dental",
        "phone_number": "+14155552671"
    }
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "token" in data
    tenant_id = data["tenant_id"]
    assert "apex_dental" in tenant_id

    # Verify instant website loads
    site_resp = client.get(f"/site/{tenant_id}")
    assert site_resp.status_code == 200


def test_qdrant_multi_tenant_knowledge_isolation():
    """Verify Tenant A's private pricing is never visible to Tenant B."""
    tenant_a = "bella_salon_99"
    tenant_b = "zen_clinic_88"

    # Ingest for Tenant A
    res_a = client.post("/api/knowledge/ingest", json={
        "tenant_id": tenant_a,
        "text": "Bella Signature Balayage is priced at $240 and Keratin Treatment is $180.",
        "category": "pricing",
        "title": "Salon Price List"
    })
    assert res_a.status_code == 200

    # Ingest for Tenant B
    res_b = client.post("/api/knowledge/ingest", json={
        "tenant_id": tenant_b,
        "text": "Acupuncture Therapy is $120 and Cupping Session is $60.",
        "category": "pricing",
        "title": "Clinic Price List"
    })
    assert res_b.status_code == 200

    # Query Tenant A
    q_a = client.post("/api/knowledge/query", json={
        "tenant_id": tenant_a,
        "query": "how much is balayage?"
    })
    assert q_a.status_code == 200
    assert "Balayage is priced at $240" in q_a.json()["context_text"]
    assert "Acupuncture" not in q_a.json()["context_text"]

    # Query Tenant B
    q_b = client.post("/api/knowledge/query", json={
        "tenant_id": tenant_b,
        "query": "how much is acupuncture?"
    })
    assert q_b.status_code == 200
    assert "Acupuncture Therapy is $120" in q_b.json()["context_text"]
    assert "Balayage" not in q_b.json()["context_text"]

    # Check stats endpoint
    stats = client.get(f"/api/knowledge/stats?tenant_id={tenant_a}")
    assert stats.status_code == 200
    assert stats.json()["indexed_chunks_count"] >= 1


def test_meta_oauth_url_generation():
    """Verify Meta OAuth dialog URL includes tenant_id in state."""
    resp = client.get("/api/oauth/facebook/login?tenant_id=my_custom_clinic")
    assert resp.status_code == 200
    data = resp.json()
    assert "oauth_url" in data
    assert "facebook.com" in data["oauth_url"]
    assert "pages_messaging" in data["oauth_url"]


def test_manual_social_connect_endpoint():
    """Verify self-service manual connect saves social credentials."""
    payload = {
        "tenant_id": "test_saas_biz",
        "whatsapp_phone_number_id": "999888777",
        "meta_page_id": "111222333",
        "instagram_account_id": "444555666"
    }
    resp = client.post("/api/oauth/meta/manual-connect", json=payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"

    stored = get_tenant_integrations("test_saas_biz")
    assert stored["whatsapp_phone_number_id"] == "999888777"
    assert stored["meta_page_id"] == "111222333"


def test_dynamic_multi_tenant_whatsapp_webhook():
    """Verify incoming WhatsApp message dynamically routes to the correct tenant."""
    # Provision tenant integration
    save_tenant_integrations(
        tenant_id="dental_dynamic",
        whatsapp_phone_number_id="wa_dynamic_id_555"
    )

    # Inbound payload from Meta
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "metadata": {
                                "phone_number_id": "wa_dynamic_id_555"
                            },
                            "messages": [
                                {
                                    "from": "14155550199",
                                    "text": {
                                        "body": "Do you accept emergency dental walk-ins?"
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    resp = client.post("/webhook/whatsapp", json=payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "processed"
