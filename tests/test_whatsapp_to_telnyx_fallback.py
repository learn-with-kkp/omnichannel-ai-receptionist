"""
Comprehensive Test Suite for Adaptive WhatsApp-First Voice Calling with Telnyx PSTN Fallback.
Validates:
1. Direct NotificationDispatcher dispatch_adaptive_voice_call logic.
2. Tier 1 WhatsApp Voice Call success path.
3. Tier 2 Automatic Fallback to Telnyx PSTN (+1 617-271-8180) when WhatsApp call fails.
4. FastAPI Endpoint /api/voice/call-whatsapp-with-telnyx-fallback.
5. Inbound Twilio WhatsApp Webhook with "call me" trigger.
6. Inbound Meta WhatsApp Webhook with "call me" trigger.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app import app
from core.notifications import notification_dispatcher

client = TestClient(app)


def test_adaptive_voice_call_tier1_whatsapp_success(monkeypatch):
    """When WhatsApp calling is available and succeeds, Tier 1 is selected with fallback_engaged=False."""
    def mock_whatsapp_call(to_phone, customer_name, tenant_name):
        return {
            "status": "initiated",
            "provider": "meta_whatsapp_calling",
            "recipient": to_phone
        }

    monkeypatch.setattr(notification_dispatcher, "trigger_whatsapp_voice_call", mock_whatsapp_call)

    res = notification_dispatcher.dispatch_adaptive_voice_call(
        to_phone="+16673070119",
        customer_name="Kishor Kumar Paroi",
        tenant_name="Luxe Salon & Spa",
        prefer_whatsapp=True
    )

    assert res["status"] == "success"
    assert res["tier_selected"] == "whatsapp_call"
    assert res["fallback_engaged"] is False
    assert res["recipient"] == "+16673070119"


def test_adaptive_voice_call_tier2_telnyx_fallback_on_failure(monkeypatch):
    """When WhatsApp calling fails or is unreachable, Tier 2 Telnyx PSTN failover engages immediately."""
    def mock_whatsapp_call_fail(to_phone, customer_name, tenant_name):
        return {
            "status": "failed",
            "provider": "whatsapp_unreachable",
            "reason": "Recipient device not connected to active WhatsApp VoIP session."
        }

    def mock_telnyx_call(to_phone, customer_name, tenant_name, first_message=None):
        return {
            "status": "success",
            "provider": "telnyx_direct",
            "caller_id": "+16172718180",
            "to": to_phone,
            "carrier": "Telnyx"
        }

    monkeypatch.setattr(notification_dispatcher, "trigger_whatsapp_voice_call", mock_whatsapp_call_fail)
    monkeypatch.setattr(notification_dispatcher, "trigger_telnyx_outbound_call", mock_telnyx_call)

    res = notification_dispatcher.dispatch_adaptive_voice_call(
        to_phone="+16673070119",
        customer_name="Kishor Kumar Paroi",
        tenant_name="Luxe Salon & Spa",
        prefer_whatsapp=True
    )

    assert res["status"] == "success"
    assert res["tier_selected"] == "telnyx_pstn"
    assert res["fallback_engaged"] is True
    assert res["caller_id"] == "+16172718180"
    assert res["agent"] == "Sophia"
    assert res["primary_attempt"]["status"] == "failed"


def test_api_endpoint_adaptive_call():
    """Verify POST /api/voice/call-whatsapp-with-telnyx-fallback endpoint returns 200 with structured fallback metadata."""
    payload = {
        "phone_number": "+16673070119",
        "caller_name": "Kishor Kumar Paroi",
        "tenant_id": "salon",
        "prefer_whatsapp": True
    }
    response = client.post("/api/voice/call-whatsapp-with-telnyx-fallback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert "tier_selected" in data["data"]
    assert "caller_id" in data["data"]


def test_twilio_whatsapp_inbound_call_intent():
    """Verify that incoming Twilio WhatsApp text 'Please call me' automatically triggers the adaptive voice dispatcher."""
    payload = {
        "Body": "Hello Sofia, can you please call me right away?",
        "From": "whatsapp:+16673070119"
    }
    response = client.post("/webhook/whatsapp", data=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["action"] == "adaptive_call_triggered"
    assert data["details"]["tier_selected"] in ("whatsapp_call", "telnyx_pstn")


def test_meta_whatsapp_inbound_call_intent():
    """Verify that incoming Meta WhatsApp JSON with 'call me' triggers the adaptive voice dispatcher."""
    payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "16673070119",
                        "text": {"body": "Hey Sofia! Can someone call me?"}
                    }],
                    "metadata": {
                        "phone_number_id": "mock_id"
                    }
                }
            }]
        }]
    }
    response = client.post("/webhook/whatsapp", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processed"
    assert data["action"] == "adaptive_call_triggered"
    assert data["details"]["tier_selected"] in ("whatsapp_call", "telnyx_pstn")
