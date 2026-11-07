"""
Unit tests for Meta Threads and Reddit Integrations.
Verifies:
- Threads Webhook Hub Challenge verification
- Threads incoming reply handling & response dispatch
- Reddit PM and Comment reply creation
- Reddit incoming webhook and inbox polling endpoints
"""

import pytest
from fastapi.testclient import TestClient
from backend.app import app
from integrations.threads_api import threads_client
from integrations.reddit_bot import reddit_client
from core.notifications import notification_dispatcher

client = TestClient(app)


def test_threads_webhook_verification():
    """Verify Meta Threads challenge returns the exact hub.challenge string."""
    import os
    token = os.getenv("THREADS_VERIFY_TOKEN", os.getenv("META_VERIFY_TOKEN", "omnichannel_threads_token_123"))
    response = client.get(
        "/webhook/threads",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": token,
            "hub.challenge": "threads_challenge_test_456"
        }
    )
    assert response.status_code == 200
    assert response.text == "threads_challenge_test_456"


def test_threads_webhook_invalid_token():
    """Verify unauthorized verification requests are rejected with 403."""
    response = client.get(
        "/webhook/threads",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong_token",
            "hub.challenge": "threads_challenge_test_456"
        }
    )
    assert response.status_code == 403


def test_threads_incoming_message_flow():
    """Verify incoming Threads mention triggers conversational response."""
    payload = {
        "entry": [
            {
                "id": "12345678",
                "changes": [
                    {
                        "field": "threads",
                        "value": {
                            "id": "post_threads_999",
                            "from": {
                                "id": "th_user_111",
                                "username": "jane_threads"
                            },
                            "text": "Hi, do you have any appointments available tomorrow at 2 PM?"
                        }
                    }
                ]
            }
        ]
    }
    response = client.post("/webhook/threads", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_threads_client_simulation():
    """Test simulated reply to a Thread when no production token is set."""
    res = threads_client.send_reply(reply_to_id="th_post_123", text="We are open 9am to 6pm!")
    assert res["status"] == "simulated"
    assert "threads_id" in res
    assert res["channel"] == "threads"


def test_reddit_incoming_webhook():
    """Test incoming Reddit message relay endpoint."""
    payload = {
        "author": "cool_redditor_42",
        "body": "Can I book a haircut for Saturday?",
        "subject": "Haircut inquiry",
        "thing_id": "t4_12345"
    }
    response = client.post("/webhook/reddit", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_reddit_client_simulation():
    """Test simulated Reddit PM and comment reply."""
    pm_res = reddit_client.send_private_message(
        recipient_username="u/test_user",
        subject="Booking confirmation",
        text="Your haircut is confirmed!"
    )
    assert pm_res["status"] == "simulated"
    assert pm_res["recipient"] == "test_user"

    cmt_res = reddit_client.reply_to_comment(
        thing_id="t1_abc123",
        text="Thanks for checking in with our salon!"
    )
    assert cmt_res["status"] == "simulated"
    assert cmt_res["parent_id"] == "t1_abc123"


def test_notification_dispatcher_threads_and_reddit():
    """Test multi-channel dispatcher handles Threads and Reddit booking confirmation."""
    booking_record = {
        "caller_name": "Sarah Connor",
        "caller_phone": "+15551234567",
        "service_name": "Balayage",
        "stylist_name": "Elena",
        "start_time": "Tomorrow at 11:00 AM",
        "booking_id": "BK-987"
    }

    res_th = notification_dispatcher.dispatch_booking_confirmation(
        booking_record=booking_record,
        channel="threads",
        recipient_id="post_th_888"
    )
    assert "threads" in res_th
    assert res_th["threads"]["status"] == "simulated"

    res_rd = notification_dispatcher.dispatch_booking_confirmation(
        booking_record=booking_record,
        channel="reddit",
        recipient_id="u/sarah_c"
    )
    assert "reddit" in res_rd
    assert res_rd["reddit"]["status"] == "simulated"
