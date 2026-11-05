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

logger = logging.getLogger("MessagingRouter")
router = APIRouter(prefix="", tags=["Messaging"])

VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "omnichannel_secure_token_123")


# --- WhatsApp Cloud API Webhooks ---

@router.get("/webhook/whatsapp")
def verify_whatsapp_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token")
):
    """Meta WhatsApp Webhook subscription verification."""
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
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

            logger.info(f"Incoming Meta WhatsApp from {from_phone}: {user_text}")

            orchestration = universal_orchestrator.process_conversation_turn(
                user_message=user_text,
                session_id=from_phone,
                tenant_id="salon",
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
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
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
                message = event.get("message", {})
                user_text = message.get("text", "")

                if user_text and sender_id:
                    logger.info(f"Incoming Messenger from PSID {sender_id}: {user_text}")
                    orchestration = universal_orchestrator.process_conversation_turn(
                        user_message=user_text,
                        session_id=sender_id,
                        tenant_id="salon",
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
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
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
                message = event.get("message", {})
                user_text = message.get("text", "")

                if user_text and sender_id:
                    logger.info(f"Incoming Instagram DM from {sender_id}: {user_text}")
                    orchestration = universal_orchestrator.process_conversation_turn(
                        user_message=user_text,
                        session_id=sender_id,
                        tenant_id="salon",
                        channel=OmniChannelType.INSTAGRAM
                    )
                    notification_dispatcher.send_instagram_dm(sender_id, orchestration["reply"])

        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error in Instagram webhook: {e}")
        return {"status": "error", "detail": str(e)}
