"""
Test Suite: n8n Workflow & Slack Bot Post-Call Escalation Engine
Verifies:
1. Integrity of n8n/workflows/sophia_post_call_escalation_engine.json workflow schema.
2. End-of-call webhook with Frustrated / Angry caller triggering Slack Bot escalation to Marcus.
3. Happy/neutral caller flow triggering 2-hour WhatsApp review and 30-day retention email.
4. Live / simulated dispatch of Slack Bot alerts, Resend retention emails, and WhatsApp messages.
"""

import os
import sys
import json
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ["SALON_DB_PATH"] = "test_n8n_escalation.db"
os.environ["TESTING"] = "true"

from backend.app import app
from backend.database import init_db, get_customer_by_phone_or_email
from core.notifications import notification_dispatcher

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_teardown():
    init_db(force=True)
    yield
    for f in ["test_n8n_escalation.db", "test_n8n_escalation_appts.xlsx"]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception:
                pass


def test_n8n_workflow_file_structure():
    """Verify JSON structure and node connections of sophia_post_call_escalation_engine.json."""
    workflow_path = BASE_DIR / "n8n" / "workflows" / "sophia_post_call_escalation_engine.json"
    assert workflow_path.exists(), "Workflow JSON file must exist"

    with open(workflow_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data.get("name") == "Sophia Salon Voice AI - Post-Call & Escalation Engine"
    nodes = {node["name"]: node for node in data.get("nodes", [])}
    
    # Required 8 nodes
    assert "Vapi End-of-Call Webhook" in nodes
    assert "Is Customer Frustrated?" in nodes
    assert "Send Slack Alert to Marcus" in nodes
    assert "Sync Lead to CRM (GHL/HubSpot)" in nodes
    assert "Wait 2 Hours (Post-Call)" in nodes
    assert "Send WhatsApp Review Request" in nodes
    assert "Wait 30 Days" in nodes
    assert "Send 30-Day Retention Email" in nodes

    # Verify Slack alert node target
    slack_node = nodes["Send Slack Alert to Marcus"]
    assert slack_node["parameters"]["channelId"]["value"] == "U0A57CPCBRC"

    # Verify connections
    connections = data.get("connections", {})
    assert "Vapi End-of-Call Webhook" in connections
    assert "Is Customer Frustrated?" in connections


def test_end_of_call_webhook_frustrated_caller_escalation():
    """Verify frustrated caller triggers Slack alert and archives call log."""
    payload = {
        "message": {
            "type": "end-of-call-report",
            "call": {
                "id": "call_test_frustrated_999",
                "customer": {
                    "name": "Elena Rostova",
                    "number": "+16175550199"
                },
                "duration": 145
            },
            "analysis": {
                "summary": "Customer expressed deep dissatisfaction with delayed appointment and asked to speak to management.",
                "structuredData": {
                    "caller_name": "Elena Rostova",
                    "caller_phone": "+16175550199",
                    "caller_email": "elena.rostova@vipguest.com",
                    "service_name": "Balayage",
                    "sentiment": "frustrated",
                    "call_outcome": "escalated",
                    "escalation_needed": True
                },
                "successEvaluation": "Fail"
            }
        }
    }

    res = client.post("/webhook/vapi-end-of-call", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()

    assert data["status"] == "success"
    assert data["is_frustrated"] is True
    assert "slack_alert" in data["escalation_engine"]
    assert data["escalation_engine"]["slack_alert"]["status"] in ("sent", "simulated")
    assert data["escalation_engine"]["slack_alert"]["channel"] in ("U0A57CPCBRC", "#manager-escalations")

    # Verify customer profile persisted
    cust = get_customer_by_phone_or_email(phone="+16175550199")
    assert cust is not None
    assert cust["full_name"] == "Elena Rostova"


def test_end_of_call_webhook_delighted_customer_flow():
    """Verify happy customer bypasses Slack alert and receives WhatsApp review + retention email."""
    payload = {
        "message": {
            "type": "end-of-call-report",
            "call": {
                "id": "call_test_happy_888",
                "customer": {
                    "name": "Lucas Vance",
                    "number": "+16175550288"
                },
                "duration": 95
            },
            "analysis": {
                "summary": "Customer booked a haircut with Marcus and was thrilled with Sophia's warm guidance.",
                "structuredData": {
                    "caller_name": "Lucas Vance",
                    "caller_phone": "+16175550288",
                    "caller_email": "lucas.vance@designer.com",
                    "service_name": "Signature Haircut",
                    "sentiment": "delighted",
                    "call_outcome": "booked",
                    "escalation_needed": False
                },
                "successEvaluation": "Pass"
            }
        }
    }

    res = client.post("/webhook/vapi-end-of-call", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()

    assert data["status"] == "success"
    assert data["is_frustrated"] is False
    assert "slack_alert" not in data["escalation_engine"]
    assert "whatsapp_review" in data["escalation_engine"]
    assert data["escalation_engine"]["whatsapp_review"]["status"] in ("sent", "simulated")
    assert "retention_email" in data["escalation_engine"]
    assert data["escalation_engine"]["retention_email"]["status"] in ("sent", "simulated")


def test_direct_slack_bot_dispatcher():
    """Verify notification_dispatcher.send_slack_alert generates expected payload and delivery."""
    res = notification_dispatcher.send_slack_alert(
        channel="U0A57CPCBRC",
        title="🚨 Marcus Urgent Alert: Test Frustration",
        message="Caller +16175550199 requires immediate manager attention."
    )
    assert res["status"] in ("sent", "simulated")
    assert res["channel"] == "U0A57CPCBRC"


def test_retention_cold_email_dispatcher():
    """Verify notification_dispatcher.send_retention_cold_email dispatches HTML touch-up reminder."""
    res = notification_dispatcher.send_retention_cold_email(
        to_email="guest@luxesalon.com",
        customer_name="Sophia Guest",
        days_since_visit=30
    )
    assert res["status"] in ("sent", "simulated")
    assert res["recipient"] == "guest@luxesalon.com"
    assert "touch-up" in res["subject"].lower()


def test_post_call_review_whatsapp_dispatcher():
    """Verify notification_dispatcher.send_post_call_review_whatsapp dispatches Google review link."""
    res = notification_dispatcher.send_post_call_review_whatsapp(
        to_phone="+16175550199",
        customer_name="Elena"
    )
    assert res["status"] in ("sent", "simulated")
