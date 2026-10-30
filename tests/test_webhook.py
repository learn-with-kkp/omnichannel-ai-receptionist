import pytest
from fastapi.testclient import TestClient
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Use isolated test DB
os.environ["SALON_DB_PATH"] = "test_salon.db"

from backend.app import app
from backend.database import init_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_teardown():
    init_db()
    yield
    if os.path.exists("test_salon.db"):
        os.remove("test_salon.db")

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_check_availability_tool():
    payload = {
        "message": {
            "toolCalls": [
                {
                    "id": "call_123",
                    "function": {
                        "name": "check_availability",
                        "arguments": {
                            "service_name": "Balayage",
                            "target_date": "2026-11-05",
                            "preferred_stylist": "Elena"
                        }
                    }
                }
            ]
        }
    }
    response = client.post("/webhook/vapi-tools", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["toolCallId"] == "call_123"
    assert "Balayage" in data["results"][0]["result"]
    assert "openings at" in data["results"][0]["result"]

def test_book_and_lookup_and_cancel_lifecycle():
    # 1. Book appointment
    book_payload = {
        "message": {
            "toolCalls": [
                {
                    "id": "call_book_456",
                    "function": {
                        "name": "book_appointment",
                        "arguments": {
                            "caller_name": "Sarah Connor",
                            "caller_phone": "+16175550199",
                            "service_name": "Womens Haircut",
                            "appointment_datetime": "2026-11-05T14:00:00",
                            "stylist_name": "Marcus"
                        }
                    }
                }
            ]
        }
    }
    book_res = client.post("/webhook/vapi-tools", json=book_payload)
    assert book_res.status_code == 200
    res_text = book_res.json()["results"][0]["result"]
    assert "Sarah Connor" in res_text
    assert "confirmed" in res_text
    assert "LUXE-" in res_text

    # 2. Lookup appointment
    lookup_payload = {
        "message": {
            "toolCalls": [
                {
                    "id": "call_lookup_789",
                    "function": {
                        "name": "lookup_appointment",
                        "arguments": {
                            "caller_phone": "+16175550199"
                        }
                    }
                }
            ]
        }
    }
    lookup_res = client.post("/webhook/vapi-tools", json=lookup_payload)
    assert lookup_res.status_code == 200
    assert "Womens Haircut" in lookup_res.json()["results"][0]["result"]

    # 3. Cancel appointment
    cancel_payload = {
        "message": {
            "toolCalls": [
                {
                    "id": "call_cancel_101",
                    "function": {
                        "name": "cancel_appointment",
                        "arguments": {
                            "caller_phone": "+16175550199"
                        }
                    }
                }
            ]
        }
    }
    cancel_res = client.post("/webhook/vapi-tools", json=cancel_payload)
    assert cancel_res.status_code == 200
    assert "successfully canceled" in cancel_res.json()["results"][0]["result"]

