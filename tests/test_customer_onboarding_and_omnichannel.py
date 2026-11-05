"""
Test Suite: Customer Onboarding, Authentication, Omnichannel Testing & Tenant Website Serving.
Covers:
- POST /api/auth/signup (Dynamic tenant auto-provisioning)
- POST /api/auth/login
- GET /api/auth/me
- POST /api/auth/change-plan ($99 Starter, $249 Growth, $599 Enterprise)
- POST /api/testing/whatsapp (Meta WhatsApp Cloud API)
- POST /api/testing/messenger (Meta Messenger Graph API)
- POST /api/testing/instagram (Instagram Direct Messages)
- POST /api/testing/voice-call (Voice Telephony Conversational Turn)
- POST /api/testing/provision-phone (Virtual Vapi/Twilio vs BYON)
- GET /api/testing/status (Channel Connectivity Monitor)
- GET /site/{tenant_id} (Customer-Facing Website)
"""

import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ["SALON_DB_PATH"] = "test_onboarding.db"
os.environ["SALON_EXCEL_PATH"] = "test_onboarding_appts.xlsx"

from backend.app import app
from backend.database import init_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_teardown():
    init_db()
    yield
    for f in ["test_onboarding.db", "test_onboarding_appts.xlsx"]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception:
                pass


def test_customer_signup_and_auto_tenant_creation():
    payload = {
        "email": "sarah@apexlegal.com",
        "password": "Password123!",
        "company_name": "Apex Legal Partners",
        "vertical": "legal",
        "phone_number": "+16175550199",
        "plan": "growth"
    }
    response = client.post("/api/auth/signup", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "token" in data
    assert data["user"]["email"] == "sarah@apexlegal.com"
    assert data["user"]["company_name"] == "Apex Legal Partners"
    assert data["user"]["plan"] == "growth"
    assert "apex_legal_partners" in data["tenant"]["id"]


def test_customer_signup_duplicate_email():
    payload = {
        "email": "marcus@primekey.com",
        "password": "Password123!",
        "company_name": "PrimeKey Properties",
        "vertical": "real_estate"
    }
    res1 = client.post("/api/auth/signup", json=payload)
    assert res1.status_code == 200

    # Second signup with same email must fail
    res2 = client.post("/api/auth/signup", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


def test_customer_signup_short_password():
    payload = {
        "email": "short@test.com",
        "password": "123",
        "company_name": "Short Pass Co"
    }
    res = client.post("/api/auth/signup", json=payload)
    assert res.status_code == 400
    assert "at least 6 characters" in res.json()["detail"]


def test_customer_login_flow():
    # Setup user
    signup_payload = {
        "email": "david@precisionauto.com",
        "password": "SecurePassword99!",
        "company_name": "Precision Auto Care",
        "vertical": "automotive"
    }
    client.post("/api/auth/signup", json=signup_payload)

    # Valid login
    login_res = client.post("/api/auth/login", json={
        "email": "david@precisionauto.com",
        "password": "SecurePassword99!"
    })
    assert login_res.status_code == 200
    token = login_res.json()["token"]
    assert token

    # Invalid password
    bad_res = client.post("/api/auth/login", json={
        "email": "david@precisionauto.com",
        "password": "WrongPassword!"
    })
    assert bad_res.status_code == 401


def test_get_profile_me():
    signup_res = client.post("/api/auth/signup", json={
        "email": "elena@luxesalon.com",
        "password": "Password123!",
        "company_name": "Luxe Salon & Spa",
        "vertical": "salon"
    })
    token = signup_res.json()["token"]

    # Authenticated me
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["user"]["email"] == "elena@luxesalon.com"
    assert me_data["user"]["plan"] == "growth"

    # Unauthenticated
    unauth_res = client.get("/api/auth/me")
    assert unauth_res.status_code == 401


def test_change_subscription_plan():
    res = client.post("/api/auth/change-plan", json={
        "tenant_id": "salon",
        "plan": "enterprise"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["plan"] == "enterprise"
    assert data["monthly_fee"] == "$599/mo"


def test_hands_on_whatsapp_testing():
    res = client.post("/api/testing/whatsapp", json={
        "tenant_id": "salon",
        "caller_name": "Jordan Bell",
        "caller_phone": "+16673070119",
        "message": "Hi, what time do you open tomorrow?"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["channel"] == "whatsapp"
    assert "bot_reply" in data
    assert "meta_payload" in data
    assert data["meta_payload"]["messaging_product"] == "whatsapp"
    assert data["latency_ms"] > 0


def test_hands_on_messenger_testing():
    res = client.post("/api/testing/messenger", json={
        "tenant_id": "salon",
        "caller_name": "Chris Morgan",
        "caller_phone": "+16673070119",
        "message": "Can I see your open appointment slots?"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["channel"] == "messenger"
    assert "messenger_payload" in data
    assert data["messenger_payload"]["recipient"]["id"] == "fb_psid_99281"


def test_hands_on_instagram_testing():
    res = client.post("/api/testing/instagram", json={
        "tenant_id": "salon",
        "caller_name": "Taylor Swift",
        "caller_phone": "+16673070119",
        "message": "Do you have balayage appointments tomorrow?"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["channel"] == "instagram"
    assert "instagram_payload" in data


def test_hands_on_telegram_testing():
    res = client.post("/api/testing/telegram", json={
        "tenant_id": "salon",
        "caller_name": "Pavel Durov",
        "caller_phone": "+16673070119",
        "message": "Can I book a consultation tomorrow at 10 AM?"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["channel"] == "telegram"
    assert "bot_reply" in data
    assert "telegram_payload" in data
    assert data["telegram_payload"]["chat_id"] == "7729104"


def test_hands_on_twitter_testing():
    res = client.post("/api/testing/twitter", json={
        "tenant_id": "salon",
        "caller_name": "Elon Musk",
        "caller_phone": "+16673070119",
        "message": "Hey what services do you offer?"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["channel"] == "twitter"
    assert "bot_reply" in data
    assert "twitter_payload" in data
    assert data["twitter_payload"]["recipient_id"] == "90124991"


def test_hands_on_linkedin_testing():
    res = client.post("/api/testing/linkedin", json={
        "tenant_id": "salon",
        "caller_name": "Satya Nadella",
        "caller_phone": "+16673070119",
        "message": "Inquiring about executive haircut slots on Friday"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["channel"] == "linkedin"
    assert "bot_reply" in data
    assert "linkedin_payload" in data
    assert "urn:li:person" in data["linkedin_payload"]["recipient"]


def test_hands_on_tiktok_testing():
    res = client.post("/api/testing/tiktok", json={
        "tenant_id": "salon",
        "caller_name": "Addison Rae",
        "caller_phone": "+16673070119",
        "message": "Loved your salon on my FYP! Can I book with Elena?"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["channel"] == "tiktok"
    assert "bot_reply" in data
    assert "tiktok_payload" in data
    assert data["tiktok_payload"]["to_user_id"] == "tt_open_id_61029"


def test_social_webhooks():
    # 1. Telegram probe
    res_tg = client.get("/webhook/telegram")
    assert res_tg.status_code == 200
    assert res_tg.json()["ready"] is True

    # 2. Twitter CRC verification
    res_tw = client.get("/webhook/twitter?crc_token=test_crc_token_12345")
    assert res_tw.status_code == 200
    assert "sha256=" in res_tw.json()["response_token"]

    # 3. TikTok verification
    res_tt = client.get("/webhook/tiktok?challenge=tiktok_challenge_99&verify_token=omnichannel_secure_token_123")
    assert res_tt.status_code == 200
    assert res_tt.text == "tiktok_challenge_99"


def test_save_and_retrieve_all_omnichannel_integrations():
    payload = {
        "tenant_id": "salon",
        "whatsapp_phone_number_id": "wa_live_123",
        "meta_page_id": "page_live_456",
        "instagram_account_id": "ig_live_789",
        "telegram_bot_token": "tg_bot_token_abc",
        "twitter_api_key": "tw_api_key_def",
        "twitter_bearer_token": "tw_bearer_ghi",
        "linkedin_client_id": "li_client_jkl",
        "linkedin_access_token": "li_token_mno",
        "tiktok_client_key": "tt_key_pqr",
        "tiktok_access_token": "tt_token_stu"
    }
    res = client.post("/api/auth/integrations", json=payload)
    assert res.status_code == 200
    data = res.json()["integrations"]
    assert data["telegram_bot_token"] == "tg_bot_token_abc"
    assert data["twitter_bearer_token"] == "tw_bearer_ghi"
    assert data["linkedin_access_token"] == "li_token_mno"
    assert data["tiktok_access_token"] == "tt_token_stu"


def test_hands_on_voice_call_testing():
    res = client.post("/api/testing/voice-call", json={
        "tenant_id": "salon",
        "caller_name": "Sarah Connor",
        "caller_phone": "+16673070119",
        "message": "I would like to schedule a haircut for tomorrow at 2pm",
        "accent": "canadian_english"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["channel"] == "voice"
    assert "bot_speech" in data
    assert "metrics" in data


def test_telephony_provisioning_auto():
    res = client.post("/api/testing/provision-phone", json={
        "tenant_id": "salon",
        "mode": "auto",
        "country": "US"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["provider"] == "vapi_twilio"
    assert data["assigned_phone_number"].startswith("+1888")
    assert "webhook_url" in data


def test_telephony_provisioning_byon():
    res = client.post("/api/testing/provision-phone", json={
        "tenant_id": "salon",
        "mode": "byon",
        "customer_phone": "+16175558833"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["provider"] == "customer_sip"
    assert data["assigned_phone_number"] == "+16175558833"


def test_testing_suite_status():
    res = client.get("/api/testing/status?tenant_id=salon")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "operational"
    assert "channels" in data
    assert data["channels"]["website_calling"]["status"] == "online"
    assert data["channels"]["whatsapp"]["status"] == "configured"
    assert data["channels"]["messenger"]["status"] == "configured"
    assert data["channels"]["instagram"]["status"] == "configured"
    assert data["channels"]["telephony"]["status"] == "active"


def test_serve_tenant_site():
    res = client.get("/site/salon")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "Sofia" in res.text

