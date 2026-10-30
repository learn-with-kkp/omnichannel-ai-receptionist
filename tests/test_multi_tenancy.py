import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pytest
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ["SALON_DB_PATH"] = "test_multitenant.db"
os.environ["SALON_EXCEL_PATH"] = "test_mt_appointments.xlsx"

from backend.app import app
from backend.database import init_db, create_tenant, get_tenant_by_inbound_phone

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_teardown():
    init_db()
    # Create two isolated salon tenants
    create_tenant(
        tenant_id="soho_cuts",
        name="SoHo Cuts NYC",
        phone="+12125559900",
        address="100 Broadway, NY",
        services=[("Fade Cut", 30, 55), ("Beard Trim", 20, 30)],
        stylists=["Leo", "Jax"]
    )
    yield
    for f in ["test_multitenant.db", "test_mt_appointments.xlsx"]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception:
                pass

def test_tenant_lookup_by_inbound_phone():
    tenant = get_tenant_by_inbound_phone("+12125559900")
    assert tenant["id"] == "soho_cuts"
    assert tenant["name"] == "SoHo Cuts NYC"

def test_multi_tenant_call_routing():
    # Call to SoHo Cuts phone number
    payload = {
        "message": {
            "call": {
                "phoneNumber": {
                    "number": "+12125559900"
                }
            },
            "toolCalls": [
                {
                    "id": "mt_call_001",
                    "function": {
                        "name": "check_availability",
                        "arguments": {
                            "service_name": "Fade Cut",
                            "target_date": "2026-11-10",
                            "preferred_stylist": "Leo"
                        }
                    }
                }
            ]
        }
    }
    response = client.post("/webhook/vapi-tools", json=payload)
    assert response.status_code == 200
    res_text = response.json()["results"][0]["result"]
    assert "SoHo Cuts NYC" in res_text
    assert "Fade Cut" in res_text

