"""
Test Suite for Nimbus-Inspired Low-Latency Voice Features,
Customer Onboarding, Real Estate & Legal Verticals, and US/Canada/Europe Dialects.
"""

import pytest
import time
from fastapi.testclient import TestClient

from backend.app import app
from core.latency import LatencyTracker
from core.audio_processor import pcm_to_wav, to_wav, calculate_audio_energy
from core.blueprint.tenant_manager import tenant_registry
from core.engine.orchestrator import universal_orchestrator

client = TestClient(app)


def test_latency_tracker_stages():
    """Verify microsecond per-stage latency tracking from Nimbus architecture."""
    tracker = LatencyTracker()
    with tracker.stage("asr"):
        time.sleep(0.01)
    with tracker.stage("rag"):
        time.sleep(0.005)
    with tracker.stage("llm_ttft"):
        time.sleep(0.008)
    with tracker.stage("llm_total"):
        time.sleep(0.015)
    with tracker.stage("tool"):
        time.sleep(0.004)
    with tracker.stage("tts"):
        time.sleep(0.01)

    breakdown = tracker.as_dict()
    assert breakdown["asr_ms"] >= 8.0
    assert breakdown["rag_ms"] >= 4.0
    assert breakdown["llm_total_ms"] >= 10.0
    assert breakdown["total_ms"] > breakdown["asr_ms"]


def test_audio_processor_helpers():
    """Verify PCM to WAV packaging and audio energy calculation."""
    # 1. PCM to WAV wrapping
    raw_pcm = b"\x00\x00" * 800  # 800 samples = 50ms at 16kHz
    wav_bytes = pcm_to_wav(raw_pcm, sample_rate=16000)
    assert wav_bytes.startswith(b"RIFF")
    assert b"WAVE" in wav_bytes[:12]
    assert len(wav_bytes) == len(raw_pcm) + 44

    # 2. to_wav pass-through
    transcoded = to_wav(wav_bytes)
    assert transcoded.startswith(b"RIFF")

    # 3. Audio RMS energy
    energy = calculate_audio_energy(raw_pcm)
    assert energy == 0.0


def test_real_estate_vertical():
    """Verify Real Estate vertical manifest, private property tour booking, and broker matching."""
    re_tenant = tenant_registry.get_tenant("real_estate")
    assert re_tenant is not None
    assert "Real Estate" in re_tenant.name or "PrimeKey" in re_tenant.name
    assert any("Showing" in s.name or "Tour" in s.name for s in re_tenant.services)
    assert any("Victoria" in st.name for st in re_tenant.staff)

    res = universal_orchestrator.process_conversation_turn(
        user_message="I'd like to book a Private Home Showing tomorrow at 2:00 PM",
        session_id="re-test-session",
        tenant_id="real_estate",
        caller_name="James Bond",
        caller_phone="+12125550007"
    )
    assert res["action_performed"] == "booked"
    assert "James Bond" in res["reply"]
    assert "PrimeKey" in res["reply"]


def test_legal_firm_vertical():
    """Verify Legal Firm vertical manifest and confidential consultation booking."""
    legal_tenant = tenant_registry.get_tenant("legal")
    assert legal_tenant is not None
    assert "Apex & Partners" in legal_tenant.name or "Legal" in legal_tenant.name
    assert any("Consultation" in s.name for s in legal_tenant.services)
    assert any("Julian" in st.name for st in legal_tenant.staff)

    res = universal_orchestrator.process_conversation_turn(
        user_message="I need a Confidential Initial Legal Consultation tomorrow at 3:00 PM",
        session_id="legal-test-session",
        tenant_id="legal",
        caller_name="Bruce Wayne",
        caller_phone="+12125559999"
    )
    assert res["action_performed"] == "booked"
    assert "Bruce Wayne" in res["reply"]
    assert "Apex & Partners" in res["reply"]


def test_target_market_dialects():
    """Verify regional English dialects for Canada, US, and Europe."""
    dialects = [
        ("canadian_english", "eh"),
        ("general_american", "Hello!"),
        ("irish_english", "Grand!"),
        ("euro_international", "Certainly!"),
        ("australian_english", "G'day!"),
    ]
    for key, phrase in dialects:
        acc = tenant_registry.get_accent(key)
        assert acc is not None
        assert acc.key == key

        res = universal_orchestrator.process_conversation_turn(
            user_message="Check openings tomorrow",
            session_id=f"test-dialect-{key}",
            tenant_id="salon",
            accent_key=key
        )
        assert res["accent"]["key"] == key
        assert phrase in res["reply"]


def test_caller_frustration_sentiment_escalation():
    """Verify that frustrated callers trigger sentiment detection and automatic manager escalation."""
    frustrated_msg = "This service is completely terrible and unacceptable! I am furious!"
    res = universal_orchestrator.process_conversation_turn(
        user_message=frustrated_msg,
        session_id="sentiment-test",
        tenant_id="salon"
    )
    assert res["sentiment"] == "frustrated"
    assert res["intent"] == "escalate"
    assert res["action_performed"] == "escalated"
    assert "transferring you directly to our front desk manager" in res["reply"]


def test_customer_self_serve_onboarding():
    """Verify 1-click dynamic tenant provisioning endpoint."""
    payload = {
        "business_name": "Vancouver Premier Dental Care",
        "vertical": "dental",
        "phone_number": "+16045550199",
        "address": "1200 Burrard St, Vancouver, BC V6Z 2C7",
        "primary_accent": "canadian_english",
        "whatsapp_phone_number_id": "9988776655",
        "meta_page_id": "11223344",
        "google_calendar_id": "vancouver_dental@gmail.com"
    }
    response = client.post("/api/blueprint/onboard-customer", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "Vancouver Premier Dental" in data["tenant"]["name"]
    assert "whatsapp_webhook" in data["webhooks"]
    assert "vancouver_premier_dental_care" in data["tenant_id"]

    # Verify dynamically registered and immediately retrievable
    retrieved = tenant_registry.get_tenant(data["tenant_id"])
    assert retrieved is not None
    assert retrieved.name == "Vancouver Premier Dental Care"


def test_barge_in_endpoint():
    """Verify instant barge-in endpoint halts audio streaming."""
    response = client.post("/api/voice/interrupt", json={"session_id": "sess-live-99", "reason": "barge_in"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "interrupted"
    assert data["action"] == "halt_playback"
