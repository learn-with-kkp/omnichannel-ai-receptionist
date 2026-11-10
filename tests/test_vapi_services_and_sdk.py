import os
import sys
import json
import pytest
import httpx
from pathlib import Path
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Use isolated test database
os.environ["SALON_DB_PATH"] = "test_vapi_services.db"
os.environ["TESTING"] = "true"

from backend.app import app
from backend.database import init_db

client = TestClient(app)

PRIVATE_KEY = os.getenv("VAPI_PRIVATE_API_KEY") or os.getenv("VAPI_API_KEY")
PUBLIC_KEY = os.getenv("VAPI_PUBLIC_API_KEY") or os.getenv("VAPI_PUBLIC")
ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID")
PHONE_ID = os.getenv("VAPI_PHONE_NUMBER_ID")

@pytest.fixture(autouse=True)
def setup_teardown():
    init_db()
    yield
    if os.path.exists("test_vapi_services.db"):
        os.remove("test_vapi_services.db")

def test_vapi_credentials_loaded():
    """Verify private and public Vapi credentials are configured."""
    assert PRIVATE_KEY, "VAPI_PRIVATE_API_KEY or VAPI_API_KEY must be configured in .env"
    assert PUBLIC_KEY, "VAPI_PUBLIC_API_KEY must be configured in .env"
    assert ASSISTANT_ID, "VAPI_ASSISTANT_ID must be configured in .env"

def test_vapi_web_sdk_config_endpoint():
    """Verify GET /api/voice/vapi-config delivers public config for Web SDK."""
    resp = client.get("/api/voice/vapi-config")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["publicKey"] == PUBLIC_KEY
    assert data["assistantId"] == ASSISTANT_ID
    assert data["sdkLoaded"] is True

def test_vapi_web_sdk_html_harness_endpoint():
    """Verify /vapi-test serves the HTML test harness."""
    resp = client.get("/vapi-test")
    assert resp.status_code == 200
    assert "Vapi Web SDK Diagnostic Test Harness" in resp.text
    assert "@vapi-ai/web" in resp.text

@pytest.mark.skipif(not PRIVATE_KEY, reason="Vapi Private Key required for live API tests")
def test_live_vapi_assistants_service():
    """Live test of Vapi Assistants Service via private key."""
    headers = {"Authorization": f"Bearer {PRIVATE_KEY}"}
    with httpx.Client(timeout=15.0) as http:
        resp = http.get("https://api.vapi.ai/assistant", headers=headers)
        assert resp.status_code == 200
        assistants = resp.json()
        assert len(assistants) > 0

        # Verify Target Assistant
        asst_resp = http.get(f"https://api.vapi.ai/assistant/{ASSISTANT_ID}", headers=headers)
        assert asst_resp.status_code == 200
        asst = asst_resp.json()
        assert asst["id"] == ASSISTANT_ID
        assert "model" in asst
        assert "voice" in asst
        assert "transcriber" in asst

@pytest.mark.skipif(not PRIVATE_KEY, reason="Vapi Private Key required for live API tests")
def test_live_vapi_phone_numbers_service():
    """Live test of Vapi Phone Numbers Service via private key."""
    headers = {"Authorization": f"Bearer {PRIVATE_KEY}"}
    with httpx.Client(timeout=15.0) as http:
        resp = http.get("https://api.vapi.ai/phone-number", headers=headers)
        assert resp.status_code == 200
        numbers = resp.json()
        assert len(numbers) > 0
        phone_ids = [n["id"] for n in numbers]
        if PHONE_ID:
            assert PHONE_ID in phone_ids

@pytest.mark.skipif(not PRIVATE_KEY, reason="Vapi Private Key required for live API tests")
def test_live_vapi_calls_and_squads_service():
    """Live test of Vapi Calls and Squads services."""
    headers = {"Authorization": f"Bearer {PRIVATE_KEY}"}
    with httpx.Client(timeout=15.0) as http:
        # Calls
        c_resp = http.get("https://api.vapi.ai/call?limit=2", headers=headers)
        assert c_resp.status_code == 200

        # Squads
        s_resp = http.get("https://api.vapi.ai/squad", headers=headers)
        assert s_resp.status_code == 200

@pytest.mark.skipif(not PUBLIC_KEY, reason="Vapi Public Key required for Web SDK test")
def test_live_vapi_web_sdk_call_engine():
    """Live test of Vapi Web SDK WebRTC call generation via public key."""
    headers = {
        "Authorization": f"Bearer {PUBLIC_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "assistantId": ASSISTANT_ID
    }
    with httpx.Client(timeout=15.0) as http:
        resp = http.post("https://api.vapi.ai/call/web", headers=headers, json=payload)
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["type"] == "webCall"
        assert "daily.co" in data.get("webCallUrl", "") or "daily" in data.get("transport", {}).get("provider", "")
        assert data.get("id") is not None

def test_vapi_tools_webhook_integration():
    """Verify synchronous tool call processing for Vapi mid-call execution."""
    payload = {
        "message": {
            "toolCalls": [
                {
                    "id": "test_call_sdk_1",
                    "function": {
                        "name": "check_availability",
                        "arguments": {
                            "service_name": "Balayage",
                            "target_date": "2026-11-06",
                            "preferred_stylist": "Elena"
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
    assert data["results"][0]["toolCallId"] == "test_call_sdk_1"
    assert "Balayage" in data["results"][0]["result"]
