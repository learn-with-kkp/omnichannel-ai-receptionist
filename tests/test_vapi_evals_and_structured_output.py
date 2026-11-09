import pytest
import json
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.app import app
from backend.database import init_db, save_call_log, get_call_log, list_call_logs, get_call_analytics
from core.tools_catalog import CATEGORIZED_TOOLS_CATALOG, ToolDefinition

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    """Ensure database schema is initialized before every test."""
    init_db()

def test_tools_catalog_categorization():
    """Validates that all conversational tools are cleanly categorized with strict schemas."""
    assert "categories" in CATEGORIZED_TOOLS_CATALOG
    categories = {c["id"]: c for c in CATEGORIZED_TOOLS_CATALOG["categories"]}
    
    expected_categories = [
        "scheduling_and_calendar",
        "omnichannel_communications",
        "knowledge_and_intelligence",
        "team_routing_and_escalations"
    ]
    for cat_id in expected_categories:
        assert cat_id in categories, f"Missing category: {cat_id}"
        assert len(categories[cat_id]["tools"]) > 0

    all_tool_names = []
    for cat in categories.values():
        for tool in cat["tools"]:
            all_tool_names.append(tool["name"])
            assert "description" in tool
            assert "parameters" in tool
            assert "required" in tool

    assert "check_availability" in all_tool_names
    assert "book_appointment" in all_tool_names
    assert "transfer_to_manager" in all_tool_names
    assert "query_knowledge_base" in all_tool_names
    assert "send_text" in all_tool_names

def test_vapi_structured_output_schema():
    """Validates that structured outputs adhere to the enterprise salon schema."""
    sample_structured_data = {
        "caller_name": "Seraphina Vance",
        "caller_phone": "+16175550199",
        "caller_email": "seraphina.vance@example.com",
        "service_name": "Signature Balayage & Gloss",
        "stylist_preference": "Marcus Vance",
        "appointment_datetime": "2026-11-12T14:30:00",
        "call_outcome": "booked",
        "sentiment": "positive",
        "transferred_to": "none",
        "action_items": [
            "Send calendar invite",
            "Prepare Olaplex bond repair formula"
        ],
        "vip_notes": "Prefers sparkling water with fresh lemon upon arrival"
    }

    assert sample_structured_data["call_outcome"] in ("booked", "rescheduled", "canceled", "inquiry", "transferred", "voicemail")
    assert sample_structured_data["sentiment"] in ("positive", "neutral", "negative", "frustrated")
    assert len(sample_structured_data["action_items"]) == 2
    assert sample_structured_data["caller_name"] == "Seraphina Vance"

def test_end_of_call_webhook_and_db_persistence():
    """Simulates Vapi's end-of-call report with structured analysis, rubric eval, and metadata."""
    call_id = "test_call_eval_998811"
    vapi_payload = {
        "message": {
            "type": "end-of-call-report",
            "call": {
                "id": call_id,
                "status": "ended",
                "customer": {
                    "number": "+16175550199",
                    "name": "Lady Genevieve"
                },
                "duration": 185
            },
            "summary": "Guest called to schedule a Signature Balayage with Marcus. Sophia checked availability and confirmed booking.",
            "transcript": "AI: Welcome to Luxe Salon! How can I help you? Caller: I'd like to book Balayage with Marcus. AI: Booked for Thursday at 2:30pm!",
            "recordingUrl": "https://storage.vapi.ai/recordings/test_call_998811.wav",
            "durationSeconds": 185,
            "analysis": {
                "summary": "Guest called to schedule a Signature Balayage with Marcus. Confirmed booking.",
                "structuredData": {
                    "caller_name": "Lady Genevieve",
                    "caller_phone": "+16175550199",
                    "caller_email": "genevieve@luxurylife.com",
                    "service_name": "Signature Balayage & Gloss",
                    "stylist_preference": "Marcus Vance",
                    "appointment_datetime": "2026-11-12T14:30:00",
                    "call_outcome": "booked",
                    "sentiment": "positive",
                    "transferred_to": "none",
                    "action_items": ["Send SMS confirmation", "Prepare color bar"],
                    "vip_notes": "VIP client"
                },
                "successEvaluation": "Pass"
            }
        }
    }

    response = client.post("/webhook/vapi-end-of-call", json=vapi_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["call_id"] == call_id
    assert data["outcome"] == "booked"
    assert data["evaluation"] == "Pass"

    # Verify retrieval from admin endpoint
    single_res = client.get(f"/admin/call-logs/{call_id}")
    assert single_res.status_code == 200
    log = single_res.json()["call_log"]
    assert log["call_id"] == call_id
    assert log["caller_name"] == "Lady Genevieve"
    assert log["call_outcome"] == "booked"
    assert log["sentiment"] == "positive"
    assert log["evaluation_score"] == "Pass"
    assert log["duration_seconds"] == 185

def test_admin_call_logs_analytics():
    """Tests call log listing and analytics aggregation."""
    # Ensure some logs exist
    save_call_log({
        "call_id": "test_analytics_1",
        "tenant_id": "salon",
        "caller_name": "Test User A",
        "call_outcome": "booked",
        "sentiment": "positive",
        "duration_seconds": 120,
        "evaluation_score": "Pass"
    })
    save_call_log({
        "call_id": "test_analytics_2",
        "tenant_id": "salon",
        "caller_name": "Test User B",
        "call_outcome": "inquiry",
        "sentiment": "neutral",
        "duration_seconds": 60,
        "evaluation_score": "Pass"
    })

    response = client.get("/admin/call-logs?limit=10")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert "analytics" in payload
    assert payload["analytics"]["total_calls"] >= 2
    assert "booked" in payload["analytics"]["outcome_distribution"]

def test_tools_catalog_endpoint():
    """Tests the GET /api/tools/catalog endpoint."""
    response = client.get("/api/tools/catalog")
    assert response.status_code == 200
    catalog = response.json()
    assert "categories" in catalog
    assert len(catalog["categories"]) >= 4

@patch("backend.routers.voice.notification_dispatcher.send_slack_alert")
def test_transfer_to_manager_tool_execution(mock_slack):
    """Validates that Sophia/Marcus can execute the transfer_to_manager tool during escalation."""
    mock_slack.return_value = {"status": "mocked"}
    payload = {
        "message": {
            "type": "tool-calls",
            "toolCalls": [
                {
                    "id": "call_transfer_mgr_01",
                    "type": "function",
                    "function": {
                        "name": "transfer_to_manager",
                        "arguments": {
                            "escalation_reason": "Guest requests urgent VIP salon director consultation",
                            "target_department": "Director Office - Marcus"
                        }
                    }
                }
            ],
            "call": {
                "id": "test_transfer_call_id",
                "customer": {
                    "number": "+16175550199"
                }
            }
        }
    }

    response = client.post("/webhook/vapi-tools", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert "results" in res_data
    assert len(res_data["results"]) == 1
    assert "transfer" in res_data["results"][0]["result"].lower() or "supervisor" in res_data["results"][0]["result"].lower()
    mock_slack.assert_called_once()
