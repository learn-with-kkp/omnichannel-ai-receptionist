"""
Voice Router: Handles WebRTC Browser Voice, Twilio Outbound Direct Calling,
Twilio Voice Webhooks, and Vapi Tool Calls.
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, Request, Response, HTTPException, Body
from pydantic import BaseModel

from core.blueprint.schema import OmniChannelType
from core.blueprint.tenant_manager import tenant_registry
from core.engine.orchestrator import universal_orchestrator
from core.notifications import notification_dispatcher
from backend.models import VapiWebhookPayload, VapiToolResponse, ToolResult
from backend.database import (
    lookup_by_phone,
    cancel_existing_appointment,
    get_tenant_by_inbound_phone,
    get_tenant,
    book_new_appointment
)

logger = logging.getLogger("VoiceRouter")
router = APIRouter(prefix="", tags=["Voice"])


class OutboundCallRequest(BaseModel):
    phone_number: str
    tenant_id: Optional[str] = "salon"
    accent: Optional[str] = "red_american"
    caller_name: Optional[str] = "Valued Client"


@router.post("/api/voice/call-user")
async def trigger_outbound_phone_call(payload: OutboundCallRequest):
    """
    Triggers an immediate outbound phone call to the customer's phone number via Twilio.
    The customer receives an automated AI receptionist call configured with the chosen
    tenant profile (Salon, Dental, Auto, Clinic) and regional female accent.
    """
    phone = payload.phone_number.strip()
    if not phone:
        raise HTTPException(status_code=400, detail="phone_number is required")

    tenant = tenant_registry.get_tenant(payload.tenant_id)
    accent = tenant_registry.get_accent(payload.accent)

    # Greeting based on accent
    if accent.key == "indian_english":
        greeting = f"Namaste {payload.caller_name}! This is Sofia, the AI receptionist from {tenant.name}. How may I assist you with your booking today?"
    elif accent.key == "african_english":
        greeting = f"Warm greetings {payload.caller_name}! Sofia here from {tenant.name}. We are delighted to call you regarding your appointment."
    elif accent.key == "red_american":
        greeting = f"Howdy {payload.caller_name}! This is Sofia from {tenant.name}. How can we help you out today?"
    elif accent.key == "european_british":
        greeting = f"Good day {payload.caller_name}. Sofia speaking on behalf of {tenant.name}. How may I be of assistance with your appointment today?"
    else:
        greeting = f"Hello {payload.caller_name}! This is Sofia, AI receptionist from {tenant.name}. How can I assist you with your booking today?"

    result = notification_dispatcher.trigger_outbound_call(
        to_phone=phone,
        twiml_say=greeting
    )

    logger.info(f"Triggered outbound call to {phone} for tenant '{tenant.id}' with accent '{accent.key}'")
    return {
        "status": "success",
        "message": f"Calling {phone} for {tenant.name}...",
        "details": result,
        "tenant_id": tenant.id,
        "accent": accent.key,
        "greeting": greeting
    }


@router.api_route("/webhook/twilio-voice", methods=["GET", "POST"])
async def twilio_voice_webhook(request: Request):
    """
    Inbound & Outbound Twilio Voice Webhook.
    Handles TwiML interactive voice dialogue using speech recognition.
    """
    form_data = {}
    try:
        form_data = await request.form()
    except Exception:
        pass

    speech_result = form_data.get("SpeechResult", "")
    caller_phone = form_data.get("From", "+16673070119")
    tenant_id = request.query_params.get("tenant_id", "salon")
    accent_key = request.query_params.get("accent", "red_american")

    tenant = tenant_registry.get_tenant(tenant_id)
    accent = tenant_registry.get_accent(accent_key)

    if speech_result:
        # User spoke - process via Orchestrator
        orchestration = universal_orchestrator.process_conversation_turn(
            user_message=str(speech_result),
            session_id=caller_phone,
            tenant_id=tenant_id,
            channel=OmniChannelType.VOICE_CALL,
            accent_key=accent_key,
            caller_phone=caller_phone
        )
        reply_text = orchestration["reply"]
    else:
        # Initial greeting
        reply_text = universal_orchestrator.format_accented_response(
            f"Welcome to {tenant.name}. I am Sofia, your AI receptionist. Would you like to book an appointment, check availability, or reschedule?",
            accent
        )

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" timeout="4" action="/webhook/twilio-voice?tenant_id={tenant_id}&amp;accent={accent_key}" method="POST">
        <Say voice="Polly.Danielle" language="en-US">{reply_text}</Say>
    </Gather>
    <Say voice="Polly.Danielle" language="en-US">Thank you for calling {tenant.name}. Have a wonderful day!</Say>
</Response>"""

    return Response(content=twiml, media_type="application/xml")


def generate_livekit_access_token(api_key: str, api_secret: str, identity: str, room_name: str) -> str:
    """Generates valid HS256 LiveKit AccessToken JWT."""
    import time
    import json
    import base64
    import hmac
    import hashlib

    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload = {
        "iss": api_key,
        "sub": identity,
        "nbf": now - 5,
        "exp": now + 86400,
        "video": {
            "room": room_name,
            "roomJoin": True,
            "canPublish": True,
            "canSubscribe": True,
            "canPublishData": True
        }
    }

    def b64url(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")

    header_b64 = b64url(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = b64url(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(api_secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    sig_b64 = b64url(signature)
    return f"{header_b64}.{payload_b64}.{sig_b64}"


@router.get("/api/voice/token")
def generate_webrtc_voice_token(
    identity: Optional[str] = "web-caller",
    tenant_id: Optional[str] = "salon",
    accent: Optional[str] = "red_american"
):
    """
    Generates WebRTC / LiveKit connection parameters for browser direct calling.
    Allows real-time microphone audio streaming with Sofia.
    """
    livekit_url = os.getenv("LIVEKIT_URL", "wss://livekit.cloud.antigravity.io")
    livekit_api_key = os.getenv("LIVEKIT_API_KEY", "devkey")
    livekit_secret = os.getenv("LIVEKIT_API_SECRET", "secret")

    tenant = tenant_registry.get_tenant(tenant_id)
    accent_profile = tenant_registry.get_accent(accent)
    room_name = f"receptionist-{tenant_id}"

    # Generate live cryptographically signed LiveKit AccessToken if credentials present
    if livekit_api_key and livekit_secret and not livekit_api_key.startswith("your_"):
        session_token = generate_livekit_access_token(
            api_key=livekit_api_key,
            api_secret=livekit_secret,
            identity=identity or "web-caller",
            room_name=room_name
        )
    else:
        session_token = f"webrtc-token-{tenant_id}-{identity}-{int(os.getpid())}"

    return {
        "status": "success",
        "livekit_url": livekit_url,
        "token": session_token,
        "room_name": room_name,
        "identity": identity,
        "tenant": {
            "id": tenant.id,
            "name": tenant.name,
            "voice_name": "Sofia"
        },
        "accent": {
            "key": accent_profile.key,
            "name": accent_profile.name,
            "elevenlabs_voice_id": accent_profile.elevenlabs_voice_id,
            "openai_voice": accent_profile.openai_voice
        }
    }


@router.post("/webhook/vapi-tools", response_model=VapiToolResponse)
async def handle_vapi_tools(payload: VapiWebhookPayload, tenant_id: Optional[str] = None):
    """
    Synchronous mid-call tool execution router for Vapi phone calls.
    Maintains 100% backward compatibility and routes through the Universal Blueprint.
    """
    message = payload.message
    tool_calls = message.toolCalls or []

    if not tool_calls:
        return VapiToolResponse(results=[])

    # Dynamic Multi-Tenant Routing via Inbound Phone Number
    inbound_phone = ""
    call_obj = message.call or {}
    if isinstance(call_obj, dict):
        phone_obj = call_obj.get("phoneNumber") or {}
        if isinstance(phone_obj, dict):
            inbound_phone = phone_obj.get("number", "")

    if not tenant_id:
        db_tenant = get_tenant_by_inbound_phone(inbound_phone)
        resolved_tenant_id = db_tenant.get("id", "salon")
        salon_name = db_tenant.get("name", "Luxe Salon & Spa")
    else:
        db_tenant = get_tenant(tenant_id)
        resolved_tenant_id = db_tenant.get("id", tenant_id)
        salon_name = db_tenant.get("name", "Luxe Salon & Spa")

    resolved_tenant = tenant_registry.get_tenant(resolved_tenant_id)
    results = []

    for tool_call in tool_calls:
        call_id = tool_call.id
        fn_name = tool_call.function.name
        args = tool_call.function.arguments
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except Exception:
                args = {}
        elif not isinstance(args, dict):
            args = {}

        logger.info(f"Vapi Tool Call: '{fn_name}' [ID: {call_id}] on Tenant: {resolved_tenant_id} ({salon_name})")

        if fn_name == "check_availability":
            service_name = args.get("service_name") or "Womens Haircut"
            target_date = args.get("target_date")
            if not target_date or target_date.strip() == "":
                target_date = "2026-11-06"
            stylist = args.get("preferred_stylist") or "any"
            srv = universal_orchestrator.fuzzy_match_service(resolved_tenant, service_name)
            st = universal_orchestrator.fuzzy_match_staff(resolved_tenant, stylist, srv)
            slots = universal_orchestrator.query_live_availability(resolved_tenant, target_date, srv, st)
            stylist_mention = f" with {stylist}" if stylist and stylist != "any" else ""
            if slots:
                res_text = (
                    f"For a {service_name}{stylist_mention} at {salon_name} on {target_date}, "
                    f"we have openings at {', '.join(slots)}. Which of those works best for you?"
                )
            else:
                res_text = f"We are fully booked for {service_name} on {target_date}. Would you like to check the following day?"
            results.append(ToolResult(toolCallId=call_id, result=res_text))

        elif fn_name == "book_appointment":
            name = args.get("caller_name") or "Valued Guest"
            phone = args.get("caller_phone") or "+16673070119"
            service_name = args.get("service_name") or "Womens Haircut"
            dt = args.get("appointment_datetime") or "2026-11-06T14:00:00"
            stylist_name = args.get("stylist_name") or "Elena"
            if stylist_name.lower() == "any":
                stylist_name = "Elena"

            booking = book_new_appointment(name, phone, service_name, dt, stylist_name, tenant_id=resolved_tenant_id)
            res_text = (
                f"You're all set, {name}! Your appointment for a {service_name} with {stylist_name} is confirmed at {salon_name} for "
                f"{booking['start_time']}. Your booking reference is {booking['booking_id']}. "
                f"A confirmation SMS has been sent to {phone}."
            )
            results.append(ToolResult(toolCallId=call_id, result=res_text))

        elif fn_name == "lookup_appointment":
            phone = args.get("caller_phone", "")
            booking = lookup_by_phone(phone, tenant_id=resolved_tenant_id)
            if booking:
                res_text = (
                    f"I found your reservation: {booking['service_name']} with {booking['stylist_name']} "
                    f"on {booking['start_time']} (Ref: {booking['booking_id']}). How would you like to modify it?"
                )
            else:
                res_text = f"I couldn't find an active reservation under {phone} at {salon_name}. Would you like me to book a new appointment for you?"
            results.append(ToolResult(toolCallId=call_id, result=res_text))

        elif fn_name == "cancel_appointment":
            phone = args.get("caller_phone", "")
            booking_id = args.get("booking_id")
            success = cancel_existing_appointment(phone, booking_id, tenant_id=resolved_tenant_id)
            if success:
                res_text = f"Your appointment has been successfully canceled at {salon_name}. No fee was charged. We hope to welcome you another time!"
            else:
                res_text = f"I could not locate an active booking to cancel under {phone}. Please check the number and let me know."
            results.append(ToolResult(toolCallId=call_id, result=res_text))

        elif fn_name == "transfer_to_manager":
            results.append(ToolResult(
                toolCallId=call_id,
                result=f"I'm connecting you directly with our front desk manager right now. Please hold for just a few seconds."
            ))

        else:
            results.append(ToolResult(toolCallId=call_id, result="Function processed successfully."))

    return VapiToolResponse(results=results)
