"""
Comprehensive Test Suite for the Universal Omnichannel AI Receptionist Blueprint.
Validates:
1. Multi-Tenant Vertical Switching (Salon, Dental, Automotive, Medical Clinic)
2. Female Voice Regional English Accent Adaptation (Indian, African, Red American, British)
3. Google Calendar Two-Way Synchronization (Availability, Create, Reschedule, Cancel)
4. Knowledge Retrieval (RAG vs RAGless mode toggling)
5. Outbound Phone Calling & WebRTC Token Generation
6. Omnichannel Message Ingestion (Website, WhatsApp, Messenger, Instagram)
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from backend.app import app
from core.blueprint.schema import OmniChannelType
from core.blueprint.tenant_manager import tenant_registry
from core.engine.orchestrator import universal_orchestrator
from core.engine.rag_engine import knowledge_engine
from integrations.google_calendar import calendar_service

client = TestClient(app)


def test_blueprint_vertical_manifests():
    """Verify that all 4 pre-configured industry verticals exist with valid services and staff."""
    verticals = ["salon", "dental", "automotive", "clinic"]
    for v_id in verticals:
        tenant = tenant_registry.get_tenant(v_id)
        assert tenant is not None
        assert tenant.id in (v_id, "salon_luxe", "dental_apex", "auto_precision", "clinic_carefirst")
        assert len(tenant.services) >= 3
        assert len(tenant.staff) >= 2
        assert tenant.business_rules.min_lead_time_hours > 0


def test_female_voice_accent_adaptation():
    """Verify regional English accent adaptations for Sofia across all 4 target dialects."""
    accents = ["indian_english", "african_english", "red_american", "european_british"]
    for acc in accents:
        profile = tenant_registry.get_accent(acc)
        assert profile is not None
        assert profile.elevenlabs_voice_id != ""
        assert profile.openai_voice == "nova"

        res = universal_orchestrator.process_conversation_turn(
            user_message="Hello, do you have any appointments tomorrow?",
            session_id=f"test-accent-{acc}",
            tenant_id="salon",
            accent_key=acc
        )
        assert res["accent"]["key"] == acc
        assert len(res["reply"]) > 10

        if acc == "indian_english":
            assert "Namaste" in res["reply"]
        elif acc == "african_english":
            assert "Warm greetings" in res["reply"]
        elif acc == "red_american":
            assert "Howdy" in res["reply"]
        elif acc == "european_british":
            assert "Splendid" in res["reply"]


def test_google_calendar_lifecycle():
    """Verify Google Calendar event creation, updating/rescheduling, and deletion."""
    test_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
    
    # 1. Check free/busy availability
    busy = calendar_service.query_free_busy(test_date)
    assert isinstance(busy, list)

    # 2. Create Event
    event = calendar_service.create_event(
        summary="Test Client Appointment",
        start_time_iso=f"{test_date}T11:00:00",
        duration_minutes=45,
        description="Balayage with Elena",
        attendee_phone="+16673070119"
    )
    event_id = event.get("id")
    assert event_id is not None
    assert event.get("summary") == "Test Client Appointment"

    # 3. Reschedule / Update Event
    updated = calendar_service.update_event(
        event_id=event_id,
        new_start_time_iso=f"{test_date}T14:30:00",
        duration_minutes=45
    )
    assert updated is True

    # 4. Cancel / Delete Event
    deleted = calendar_service.delete_event(event_id)
    assert deleted is True


def test_rag_vs_ragless_toggle():
    """Test switching between instant RAGless mode and semantic RAG mode."""
    # 1. RAGless Mode (<1ms)
    knowledge_engine.set_rag_mode(False)
    res_ragless = client.post("/api/blueprint/set-rag", json={"enabled": False})
    assert res_ragless.status_code == 200
    assert res_ragless.json()["rag_mode"] is False

    ctx_ragless = knowledge_engine.query_context(tenant_registry.get_tenant("dental"), "teeth cleaning")
    assert ctx_ragless["mode"] == "ragless"
    assert "Apex Dental" in ctx_ragless["context_text"]
    assert ctx_ragless["retrieval_ms"] < 15.0

    # 2. Semantic RAG Mode
    res_rag = client.post("/api/blueprint/set-rag", json={"enabled": True})
    assert res_rag.status_code == 200
    assert res_rag.json()["rag_mode"] is True

    ctx_rag = knowledge_engine.query_context(tenant_registry.get_tenant("dental"), "What is the cost of teeth cleaning?")
    assert ctx_rag["mode"] == "rag"
    assert "Apex Dental" in ctx_rag["context_text"] or "Prophylaxis" in ctx_rag["context_text"]


def test_omnichannel_chat_booking_flow():
    """Test natural language booking via the unified chat message endpoint."""
    payload = {
        "message": "Can I book a Prophylaxis Cleaning tomorrow at 2:00 PM?",
        "tenant_id": "dental",
        "accent": "european_british",
        "caller_name": "Dr. Watson",
        "caller_phone": "+16175558888",
        "channel": "website_chat"
    }
    response = client.post("/api/chat/message", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["action_performed"] == "booked"
    assert data["booking"]["booking_id"] is not None
    assert "Dr. Watson" in data["reply"]
    assert "Apex Dental" in data["reply"]


def test_outbound_call_endpoint():
    """Test triggering an outbound voice phone call to user's phone via Twilio."""
    payload = {
        "phone_number": "+16673070119",
        "tenant_id": "automotive",
        "accent": "red_american",
        "caller_name": "Sarah Connor"
    }
    response = client.post("/api/voice/call-user", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "Calling +16673070119" in data["message"]
    assert data["tenant_id"] in ("automotive", "auto_precision")


def test_webrtc_token_generation():
    """Test generating WebRTC browser microphone calling token."""
    response = client.get("/api/voice/token?tenant_id=clinic&accent=african_english")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "token" in data
    assert data["tenant"]["id"] in ("clinic", "clinic_carefirst")
    assert data["accent"]["key"] == "african_english"


def test_meta_webhook_verification():
    """Test Hub challenge verification for WhatsApp, Messenger, and Instagram."""
    import os
    token = os.getenv("META_VERIFY_TOKEN", "omnichannel_secure_token_123")

    # WhatsApp
    wa_res = client.get(f"/webhook/whatsapp?hub.mode=subscribe&hub.challenge=test_wa_challenge&hub.verify_token={token}")
    assert wa_res.status_code == 200
    assert wa_res.text == "test_wa_challenge"

    # Messenger
    fb_res = client.get(f"/webhook/messenger?hub.mode=subscribe&hub.challenge=test_fb_challenge&hub.verify_token={token}")
    assert fb_res.status_code == 200
    assert fb_res.text == "test_fb_challenge"

    # Instagram
    ig_res = client.get(f"/webhook/instagram?hub.mode=subscribe&hub.challenge=test_ig_challenge&hub.verify_token={token}")
    assert ig_res.status_code == 200
    assert ig_res.text == "test_ig_challenge"


def test_vapi_outbound_call_endpoint(monkeypatch):
    """Test triggering an outbound call via Vapi API with ElevenLabs voice synthesis."""
    from unittest.mock import MagicMock
    import requests

    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.json.return_value = {
        "id": "vapi-call-test-999",
        "status": "queued",
        "assistantId": "47b92dd7-6751-4c12-b531-23adf3614d35"
    }

    monkeypatch.setattr(requests, "post", lambda url, **kwargs: mock_resp)

    payload = {
        "phone_number": "+16673070119",
        "tenant_id": "salon",
        "caller_name": "Test Client"
    }
    response = client.post("/api/voice/vapi-call", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["call_id"] == "vapi-call-test-999"
    assert "Calling" in data["message"] or "placed" in data["message"]
