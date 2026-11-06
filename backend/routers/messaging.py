"""
Omnichannel Messaging Router:
- Meta WhatsApp Cloud API & Twilio WhatsApp
- Meta Facebook Messenger Graph API
- Meta Instagram Direct Messaging API
Provides Webhook verification (hub challenge) and bidirectional auto-response.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, Response, HTTPException, Query
from pydantic import BaseModel

from core.blueprint.schema import OmniChannelType
from core.blueprint.tenant_manager import tenant_registry
from core.engine.orchestrator import universal_orchestrator
from core.notifications import notification_dispatcher
from backend.database import lookup_tenant_by_integration_id

logger = logging.getLogger("MessagingRouter")
router = APIRouter(prefix="", tags=["Messaging"])

VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "omnichannel_secure_token_123")
VALID_VERIFY_TOKENS = {
    VERIFY_TOKEN,
    "omnichannel_sec_9e2f4b810d7a46c3b5a19e8",
    "omnichannel_secure_token_123",
    "omnichannel_threads_token_123"
}


# --- WhatsApp Cloud API Webhooks ---

@router.get("/webhook/whatsapp")
def verify_whatsapp_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token")
):
    """Meta WhatsApp Webhook subscription verification."""
    if hub_mode == "subscribe" and (hub_verify_token in VALID_VERIFY_TOKENS or hub_verify_token == VERIFY_TOKEN):
        logger.info("✅ Meta WhatsApp webhook verified successfully.")
        return Response(content=hub_challenge or "", media_type="text/plain")
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook/whatsapp")
async def handle_whatsapp_incoming(request: Request):
    """
    Receives incoming WhatsApp messages from Meta Cloud API or Twilio.
    Processes message through Universal Orchestrator and dispatches conversational reply.
    """
    content_type = request.headers.get("content-type", "")
    
    # 1. Twilio WhatsApp Form POST
    if "application/x-www-form-urlencoded" in content_type:
        form = await request.form()
        incoming_msg = form.get("Body", "")
        from_number = form.get("From", "").replace("whatsapp:", "")
        logger.info(f"Incoming Twilio WhatsApp from {from_number}: {incoming_msg}")

        orchestration = universal_orchestrator.process_conversation_turn(
            user_message=incoming_msg,
            session_id=from_number,
            tenant_id="salon",
            channel=OmniChannelType.WHATSAPP,
            caller_phone=from_number
        )
        notification_dispatcher.send_whatsapp(from_number, orchestration["reply"])
        return {"status": "success", "channel": "whatsapp_twilio"}

    # 2. Meta WhatsApp Cloud API JSON
    try:
        data = await request.json()
        entry = data.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if messages:
            msg_obj = messages[0]
            from_phone = msg_obj.get("from", "")
            user_text = msg_obj.get("text", {}).get("body", "")
            phone_num_id = value.get("metadata", {}).get("phone_number_id", "")
            resolved_tenant = lookup_tenant_by_integration_id("whatsapp_phone_number_id", phone_num_id)

            logger.info(f"Incoming Meta WhatsApp for tenant [{resolved_tenant}] from {from_phone}: {user_text}")

            orchestration = universal_orchestrator.process_conversation_turn(
                user_message=user_text,
                session_id=from_phone,
                tenant_id=resolved_tenant,
                channel=OmniChannelType.WHATSAPP,
                caller_phone=from_phone
            )

            quick_replies = orchestration.get("suggested_slots") or ["Confirm", "Reschedule", "Cancel"]
            notification_dispatcher.send_whatsapp(from_phone, orchestration["reply"], quick_replies=quick_replies)

        return {"status": "processed"}
    except Exception as e:
        logger.error(f"Error handling WhatsApp payload: {e}")
        return {"status": "error", "detail": str(e)}


# --- Facebook Messenger Webhooks ---

@router.get("/webhook/messenger")
def verify_messenger_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token")
):
    """Facebook Messenger Webhook subscription verification."""
    if hub_mode == "subscribe" and (hub_verify_token in VALID_VERIFY_TOKENS or hub_verify_token == VERIFY_TOKEN):
        logger.info("✅ Facebook Messenger webhook verified successfully.")
        return Response(content=hub_challenge or "", media_type="text/plain")
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook/messenger")
async def handle_messenger_incoming(request: Request):
    """Processes incoming Facebook Messenger messages and replies via Graph API."""
    try:
        data = await request.json()
        for entry in data.get("entry", []):
            for event in entry.get("messaging", []):
                sender_id = event.get("sender", {}).get("id")
                recipient_id = event.get("recipient", {}).get("id", "")
                resolved_tenant = lookup_tenant_by_integration_id("meta_page_id", recipient_id)
                message = event.get("message", {})
                user_text = message.get("text", "")

                if user_text and sender_id:
                    logger.info(f"Incoming Messenger for tenant [{resolved_tenant}] from PSID {sender_id}: {user_text}")
                    orchestration = universal_orchestrator.process_conversation_turn(
                        user_message=user_text,
                        session_id=sender_id,
                        tenant_id=resolved_tenant,
                        channel=OmniChannelType.MESSENGER
                    )
                    quick_replies = orchestration.get("suggested_slots") or ["Book Appointment", "Check Hours"]
                    notification_dispatcher.send_messenger(sender_id, orchestration["reply"], quick_replies=quick_replies)

        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error in Messenger webhook: {e}")
        return {"status": "error", "detail": str(e)}


# --- Instagram Direct Webhooks ---

@router.get("/webhook/instagram")
def verify_instagram_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token")
):
    """Instagram Direct Messaging webhook verification."""
    if hub_mode == "subscribe" and (hub_verify_token in VALID_VERIFY_TOKENS or hub_verify_token == VERIFY_TOKEN):
        logger.info("✅ Instagram webhook verified successfully.")
        return Response(content=hub_challenge or "", media_type="text/plain")
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook/instagram")
async def handle_instagram_incoming(request: Request):
    """Processes incoming Instagram Direct messages and auto-responds."""
    try:
        data = await request.json()
        for entry in data.get("entry", []):
            for event in entry.get("messaging", []):
                sender_id = event.get("sender", {}).get("id")
                recipient_id = event.get("recipient", {}).get("id", "")
                resolved_tenant = lookup_tenant_by_integration_id("instagram_account_id", recipient_id)
                message = event.get("message", {})
                user_text = message.get("text", "")

                if user_text and sender_id:
                    logger.info(f"Incoming Instagram DM for tenant [{resolved_tenant}] from {sender_id}: {user_text}")
                    orchestration = universal_orchestrator.process_conversation_turn(
                        user_message=user_text,
                        session_id=sender_id,
                        tenant_id=resolved_tenant,
                        channel=OmniChannelType.INSTAGRAM
                    )
                    notification_dispatcher.send_instagram_dm(sender_id, orchestration["reply"])

        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error in Instagram webhook: {e}")
        return {"status": "error", "detail": str(e)}


# --- Telegram Webhooks ---

@router.get("/webhook/telegram")
@router.get("/api/webhook/telegram")
@router.get("/api/messaging/telegram/webhook")
def verify_telegram_webhook():
    """Telegram Webhook health probe."""
    return {"status": "ok", "service": "Telegram Webhook Receiver", "ready": True}


@router.post("/webhook/telegram")
@router.post("/api/webhook/telegram")
@router.post("/api/messaging/telegram/webhook")
async def handle_telegram_incoming(request: Request, tenant_id: Optional[str] = "salon"):
    """
    Receives Telegram Bot updates (messages & inline button callback queries).
    Executes conversational turn and auto-responds via Telegram Bot API.
    """
    try:
        from integrations.telegram_bot import telegram_client
        data = await request.json()
        parsed = telegram_client.parse_incoming_update(data)
        if parsed and parsed.get("text"):
            chat_id = parsed["chat_id"]
            user_text = parsed["text"]
            user_name = parsed["user_name"]

            logger.info(f"Incoming Telegram from {user_name} ({chat_id}): {user_text}")

            orchestration = universal_orchestrator.process_conversation_turn(
                user_message=user_text,
                session_id=f"tg-{chat_id}",
                tenant_id=tenant_id or "salon",
                channel=OmniChannelType.TELEGRAM,
                caller_name=user_name
            )

            quick_replies = orchestration.get("suggested_slots") or ["Book Appointment", "Check Hours"]
            notification_dispatcher.send_telegram(chat_id, orchestration["reply"], quick_replies=quick_replies)

        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error in Telegram webhook: {e}")
        return {"status": "error", "detail": str(e)}


# --- Twitter / X Account Activity API Webhooks ---

@router.get("/webhook/twitter")
@router.get("/api/webhook/twitter")
@router.get("/api/messaging/twitter/webhook")
def verify_twitter_crc(crc_token: Optional[str] = Query(None)):
    """
    Twitter Webhook CRC Challenge:
    Responds to Twitter CRC challenge with HMAC-SHA256 signature.
    """
    from integrations.twitter_x import twitter_client
    if not crc_token:
        raise HTTPException(status_code=400, detail="Missing crc_token parameter")

    response_token = twitter_client.compute_crc_response(crc_token)
    logger.info("✅ Twitter Webhook CRC challenge responded successfully.")
    return {"response_token": response_token}


@router.post("/webhook/twitter")
@router.post("/api/webhook/twitter")
@router.post("/api/messaging/twitter/webhook")
async def handle_twitter_incoming(request: Request, tenant_id: Optional[str] = "salon"):
    """
    Receives Twitter Direct Message events and auto-responds.
    """
    try:
        from integrations.twitter_x import twitter_client
        data = await request.json()
        parsed = twitter_client.parse_incoming_dm(data)
        if parsed and parsed.get("text"):
            sender_id = parsed["sender_id"]
            user_text = parsed["text"]

            logger.info(f"Incoming Twitter DM from {sender_id}: {user_text}")

            orchestration = universal_orchestrator.process_conversation_turn(
                user_message=user_text,
                session_id=f"tw-{sender_id}",
                tenant_id=tenant_id or "salon",
                channel=OmniChannelType.TWITTER
            )

            quick_replies = orchestration.get("suggested_slots") or ["Book Appointment", "Pricing"]
            notification_dispatcher.send_twitter_dm(sender_id, orchestration["reply"], quick_replies=quick_replies)

        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error in Twitter webhook: {e}")
        return {"status": "error", "detail": str(e)}


# --- LinkedIn Messaging Webhooks ---

@router.post("/webhook/linkedin")
@router.post("/api/webhook/linkedin")
@router.post("/api/messaging/linkedin/webhook")
async def handle_linkedin_incoming(request: Request, tenant_id: Optional[str] = "salon"):
    """
    Processes incoming LinkedIn Direct Messages and auto-responds.
    """
    try:
        from integrations.linkedin_msg import linkedin_client
        data = await request.json()
        parsed = linkedin_client.parse_incoming_message(data)
        if parsed and parsed.get("text"):
            sender_urn = parsed["sender"]
            user_text = parsed["text"]

            logger.info(f"Incoming LinkedIn message from {sender_urn}: {user_text}")

            orchestration = universal_orchestrator.process_conversation_turn(
                user_message=user_text,
                session_id=f"li-{sender_urn}",
                tenant_id=tenant_id or "salon",
                channel=OmniChannelType.LINKEDIN
            )

            notification_dispatcher.send_linkedin_message(sender_urn, orchestration["reply"])

        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error in LinkedIn webhook: {e}")
        return {"status": "error", "detail": str(e)}


# --- TikTok Direct Messaging Webhooks ---

@router.get("/webhook/tiktok")
@router.get("/api/webhook/tiktok")
@router.get("/api/messaging/tiktok/webhook")
def verify_tiktok_webhook(
    challenge: Optional[str] = Query(None),
    verify_token: Optional[str] = Query(None)
):
    """TikTok webhook verification challenge."""
    if verify_token and verify_token != VERIFY_TOKEN:
        raise HTTPException(status_code=403, detail="Verification failed")
    return Response(content=challenge or "ok", media_type="text/plain")


@router.post("/webhook/tiktok")
@router.post("/api/webhook/tiktok")
@router.post("/api/messaging/tiktok/webhook")
async def handle_tiktok_incoming(request: Request, tenant_id: Optional[str] = "salon"):
    """
    Processes incoming TikTok Direct Messages and auto-responds.
    """
    try:
        from integrations.tiktok_msg import tiktok_client
        data = await request.json()
        parsed = tiktok_client.parse_incoming_dm(data)
        if parsed and parsed.get("text"):
            sender_id = parsed["sender_id"]
            user_text = parsed["text"]

            logger.info(f"Incoming TikTok DM from {sender_id}: {user_text}")

            orchestration = universal_orchestrator.process_conversation_turn(
                user_message=user_text,
                session_id=f"tt-{sender_id}",
                tenant_id=tenant_id or "salon",
                channel=OmniChannelType.TIKTOK
            )

            notification_dispatcher.send_tiktok_dm(sender_id, orchestration["reply"])

        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error in TikTok webhook: {e}")
        return {"status": "error", "detail": str(e)}


# --- Meta Threads Webhooks ---

@router.get("/webhook/threads")
def verify_threads_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge")
):
    """Meta Webhook Verification for Threads Subscriptions."""
    from integrations.threads_api import threads_client
    challenge = threads_client.verify_webhook(hub_mode, hub_verify_token, hub_challenge)
    if challenge:
        return Response(content=challenge, media_type="text/plain")
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook/threads")
async def handle_threads_incoming(request: Request, tenant_id: Optional[str] = "salon"):
    """
    Processes incoming Meta Threads mentions or replies and auto-responds via Threads API.
    """
    try:
        from integrations.threads_api import threads_client
        data = await request.json()
        parsed = threads_client.parse_incoming_webhook(data)
        if parsed and parsed.get("text"):
            post_id = parsed["post_id"]
            user_id = parsed["user_id"]
            user_text = parsed["text"]

            logger.info(f"Incoming Threads mention/reply on {post_id} by {user_id}: {user_text}")

            orchestration = universal_orchestrator.process_conversation_turn(
                user_message=user_text,
                session_id=f"th-{user_id}",
                tenant_id=tenant_id or "salon",
                channel=OmniChannelType.THREADS
            )

            notification_dispatcher.send_threads_reply(post_id, orchestration["reply"])

        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error in Threads webhook: {e}")
        return {"status": "error", "detail": str(e)}


# --- Reddit Inbound & Webhook Integration ---

@router.post("/webhook/reddit")
async def handle_reddit_incoming(request: Request, tenant_id: Optional[str] = "salon"):
    """
    Handles incoming Reddit message webhook (or relay service like Zapier/Pipedream/Custom daemon).
    Payload: {"author": "username", "body": "text", "subject": "optional", "thing_id": "optional"}
    """
    try:
        data = await request.json()
        sender_username = data.get("author") or data.get("sender") or data.get("from")
        user_text = data.get("body") or data.get("text")
        thing_id = data.get("thing_id") or data.get("id")

        if sender_username and user_text:
            logger.info(f"Incoming Reddit message from u/{sender_username}: {user_text}")

            orchestration = universal_orchestrator.process_conversation_turn(
                user_message=user_text,
                session_id=f"rd-{sender_username}",
                tenant_id=tenant_id or "salon",
                channel=OmniChannelType.REDDIT
            )

            # Reply to specific comment or private message
            target = thing_id if (thing_id and (thing_id.startswith("t1_") or thing_id.startswith("t3_"))) else sender_username
            notification_dispatcher.send_reddit_message(target, orchestration["reply"])

        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error in Reddit incoming handler: {e}")
        return {"status": "error", "detail": str(e)}


@router.post("/api/reddit/poll-inbox")
def poll_reddit_inbox(tenant_id: Optional[str] = "salon"):
    """
    Actively checks Reddit unread inbox messages, processes bookings, and auto-replies.
    Useful for serverless cron or periodic execution.
    """
    from integrations.reddit_bot import reddit_client
    unread = reddit_client.get_unread_messages(mark_read=True)
    replies_sent = []

    for msg in unread:
        author = msg.get("author")
        body = msg.get("body")
        name = msg.get("name") # e.g. t4_xyz
        if author and body:
            orchestration = universal_orchestrator.process_conversation_turn(
                user_message=body,
                session_id=f"rd-{author}",
                tenant_id=tenant_id or "salon",
                channel=OmniChannelType.REDDIT
            )
            res = notification_dispatcher.send_reddit_message(author, orchestration["reply"])
            replies_sent.append({"to": author, "status": res.get("status")})

    return {"status": "success", "messages_processed": len(replies_sent), "replies": replies_sent}


