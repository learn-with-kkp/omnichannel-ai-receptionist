import pytest
import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Use isolated test database
os.environ["SALON_DB_PATH"] = "test_vapi_suite.db"
os.environ["TESTING"] = "true"

from backend.app import app
from backend.database import init_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_teardown():
    init_db()
    yield
    if os.path.exists("test_vapi_suite.db"):
        os.remove("test_vapi_suite.db")

def test_vapi_phone_tools_send_text():
    """Verify Send Text (SMS) tool."""
    payload = {
        "message": {
            "toolCalls": [
                {
                    "id": "call_sms_1",
                    "function": {
                        "name": "send_text",
                        "arguments": {
                            "recipient_phone": "+16673070119",
                            "message_text": "Here is your booking confirmation link: https://luxe.salon/c/123",
                            "booking_id": "LUXE-7777"
                        }
                    }
                }
            ]
        }
    }
    resp = client.post("/webhook/vapi-tools", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["toolCallId"] == "call_sms_1"
    assert "sent a text message" in data["results"][0]["result"]

def test_vapi_phone_tools_transfer_call():
    """Verify Transfer Call tool with human handoff."""
    payload = {
        "message": {
            "toolCalls": [
                {
                    "id": "call_transfer_1",
                    "function": {
                        "name": "transfer_call",
                        "arguments": {
                            "escalation_reason": "Customer needs custom wedding party styling packages",
                            "target_department": "Front Desk Supervisor"
                        }
                    }
                }
            ]
        }
    }
    resp = client.post("/webhook/vapi-tools", json=payload)
    assert resp.status_code == 200
    result = resp.json()["results"][0]["result"]
    assert "transferring you directly to our front desk supervisor" in result

def test_vapi_phone_tools_end_call():
    """Verify Hang Up / End Call tool."""
    payload = {
        "message": {
            "toolCalls": [
                {
                    "id": "call_end_1",
                    "function": {
                        "name": "end_call",
                        "arguments": {
                            "closing_message": "Thank you for choosing Luxe Salon. Goodbye!"
                        }
                    }
                }
            ]
        }
    }
    resp = client.post("/webhook/vapi-tools", json=payload)
    assert resp.status_code == 200
    assert "Goodbye!" in resp.json()["results"][0]["result"]

def test_vapi_phone_tools_voicemail():
    """Verify Leave Voicemail tool."""
    payload = {
        "message": {
            "toolCalls": [
                {
                    "id": "call_vm_1",
                    "function": {
                        "name": "leave_voicemail",
                        "arguments": {
                            "customer_name": "Jessica Alba",
                            "callback_number": "+18005550199"
                        }
                    }
                }
            ]
        }
    }
    resp = client.post("/webhook/vapi-tools", json=payload)
    assert resp.status_code == 200
    result = resp.json()["results"][0]["result"]
    assert "Jessica Alba" in result
    assert "Sofia from" in result
    assert "give us a call back" in result

def test_vapi_phone_tools_dtmf():
    """Verify DTMF touch-tone transmission tool."""
    payload = {
        "message": {
            "toolCalls": [
                {
                    "id": "call_dtmf_1",
                    "function": {
                        "name": "send_dtmf",
                        "arguments": {
                            "digits": "12#"
                        }
                    }
                }
            ]
        }
    }
    resp = client.post("/webhook/vapi-tools", json=payload)
    assert resp.status_code == 200
    assert "Keypad tone '12#' has been transmitted" in resp.json()["results"][0]["result"]

def test_vapi_assistant_tools_handoff():
    """Verify Assistant Handoff tool."""
    payload = {
        "message": {
            "toolCalls": [
                {
                    "id": "call_handoff_1",
                    "function": {
                        "name": "handoff_assistant",
                        "arguments": {
                            "target_assistant": "Master Colorist Specialist",
                            "reason": "Intricate Balayage color correction consultation"
                        }
                    }
                }
            ]
        }
    }
    resp = client.post("/webhook/vapi-tools", json=payload)
    assert resp.status_code == 200
    assert "Master Colorist Specialist" in resp.json()["results"][0]["result"]

def test_vapi_assistant_tools_query_faq():
    """Verify Query / Knowledge Base tool for Business FAQs."""
    payload = {
        "message": {
            "toolCalls": [
                {
                    "id": "call_query_1",
                    "function": {
                        "name": "query_knowledge_base",
                        "arguments": {
                            "query": "Where do I park my car when visiting?"
                        }
                    }
                }
            ]
        }
    }
    resp = client.post("/webhook/vapi-tools", json=payload)
    assert resp.status_code == 200
    result = resp.json()["results"][0]["result"]
    assert "parking" in result.lower()

def test_vapi_integrations_slack():
    """Verify Slack notification integration tool."""
    payload = {
        "message": {
            "toolCalls": [
                {
                    "id": "call_slack_1",
                    "function": {
                        "name": "slack_notification",
                        "arguments": {
                            "channel": "#appointments",
                            "message": "New VIP appointment booked for Sarah Connor at 2:00 PM",
                            "title": "VIP Client Booking"
                        }
                    }
                }
            ]
        }
    }
    resp = client.post("/webhook/vapi-tools", json=payload)
    assert resp.status_code == 200
    assert "Front desk staff has been notified on Slack" in resp.json()["results"][0]["result"]

def test_vapi_integrations_gohighlevel():
    """Verify GoHighLevel CRM synchronization tool."""
    payload = {
        "message": {
            "toolCalls": [
                {
                    "id": "call_ghl_1",
                    "function": {
                        "name": "gohighlevel_sync",
                        "arguments": {
                            "contact_name": "Marcus Aurelius",
                            "contact_phone": "+16673070119",
                            "pipeline_stage": "Appointment Booked"
                        }
                    }
                }
            ]
        }
    }
    resp = client.post("/webhook/vapi-tools", json=payload)
    assert resp.status_code == 200
    assert "GoHighLevel CRM" in resp.json()["results"][0]["result"]

def test_vapi_integrations_google_sheets_and_calendar():
    """Verify Google Sheets and Google Calendar synchronization tools."""
    payload = {
        "message": {
            "toolCalls": [
                {
                    "id": "call_sheets_1",
                    "function": {
                        "name": "google_sheets_sync",
                        "arguments": {
                            "booking_id": "LUXE-9090",
                            "caller_name": "Diana Prince",
                            "service_name": "Balayage"
                        }
                    }
                },
                {
                    "id": "call_cal_1",
                    "function": {
                        "name": "google_calendar_sync",
                        "arguments": {
                            "action": "sync"
                        }
                    }
                }
            ]
        }
    }
    resp = client.post("/webhook/vapi-tools", json=payload)
    assert resp.status_code == 200
    data = resp.json()["results"]
    assert len(data) == 2
    assert "Google Sheets" in data[0]["result"]
    assert "Google Calendar" in data[1]["result"]

