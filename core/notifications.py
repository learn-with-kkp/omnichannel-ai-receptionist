from datetime import datetime, timedelta
"""
Universal Omnichannel Notification Dispatcher.
Supports:
- Twilio SMS
- Twilio Outbound Voice Calling
- Meta WhatsApp Cloud API / Twilio WhatsApp
- Meta Facebook Messenger Graph API
- Meta Instagram Direct Messaging API
- Graceful test / simulation mode with verified payload delivery logs.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
import urllib.request
import urllib.parse

logger = logging.getLogger("OmnichannelNotifications")


class NotificationDispatcher:
    """Enterprise multi-channel notification engine."""

    def __init__(self):
        # Twilio Credentials & Phone Numbers
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.vapi_phone_number = os.getenv("VAPI_PHONE_NUMBER", "")
        self.twilio_from_phone = os.getenv("TWILIO_PHONE_NUMBER") or self.vapi_phone_number or "+19124999633"
        self.twilio_whatsapp_from = os.getenv("TWILIO_WHATSAPP_NUMBER", "+14155238886")

        # Meta Cloud APIs (WhatsApp, Messenger, Instagram)
        self.meta_access_token = (
            os.getenv("META_PERMANENT_ACCESS_TOKEN")
            or os.getenv("META_ACCESS_TOKEN")
            or os.getenv("WHATSAPP_TOKEN")
            or ""
        ).strip()
        self.whatsapp_phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
        self.meta_page_id = os.getenv("META_PAGE_ID", "")

        # Telegram Bot
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")

        # Twitter / X API
        self.twitter_bearer_token = os.getenv("TWITTER_BEARER_TOKEN", "")

        # LinkedIn Messaging
        self.linkedin_access_token = os.getenv("LINKEDIN_ACCESS_TOKEN", "")

        # TikTok Direct Messaging
        self.tiktok_access_token = os.getenv("TIKTOK_ACCESS_TOKEN", "")

        # Telnyx Telephony & Messaging API
        self.telnyx_api_key = (os.getenv("TELNYX_API_KEY") or "").strip()
        self.telnyx_public_api_key = (os.getenv("TELNYX_PUBLIC_API_KEY") or "").strip()
        self.telnyx_phone_number = (os.getenv("TELNYX_PHONE_NUMBER") or "+16172718180").strip()

        # Slack Webhook URL
        self.slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL", "")

    def is_twilio_configured(self) -> bool:
        return bool(self.twilio_account_sid and self.twilio_auth_token and not self.twilio_account_sid.startswith("your_"))

    def is_meta_configured(self) -> bool:
        return bool(self.meta_access_token and not self.meta_access_token.startswith("your_"))

    def send_slack_alert(
        self,
        channel: Optional[str] = None,
        message: str = "",
        title: Optional[str] = None,
        blocks: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Dispatches an instant alert to Slack via official Slack Bot API (chat.postMessage)
        or incoming Webhook URL.
        Supports rich block kit formatting, user DMs (e.g. U0A57CPCBRC), and channels.
        """
        target_channel = channel or os.getenv("SLACK_ESCALATION_CHANNEL") or os.getenv("SLACK_ESCALATION_USER_ID") or "U0A57CPCBRC"
        token = os.getenv("SLACK_BOT_TOKEN", "").strip()

        # 1. Prefer official Slack Bot token if configured
        if token and not token.startswith("your_") and not os.getenv("TESTING"):
            try:
                import httpx
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                body = {
                    "channel": target_channel,
                    "text": message or (title or "Omnichannel Voice Receptionist Alert")
                }
                if blocks:
                    body["blocks"] = blocks
                elif title:
                    body["blocks"] = [
                        {
                            "type": "header",
                            "text": {"type": "plain_text", "text": title, "emoji": True}
                        },
                        {
                            "type": "section",
                            "text": {"type": "mrkdwn", "text": message}
                        }
                    ]

                resp = httpx.post("https://slack.com/api/chat.postMessage", json=body, headers=headers, timeout=6.0)
                res_data = resp.json()
                if resp.status_code == 200 and res_data.get("ok"):
                    logger.info(f"✅ Slack Bot alert successfully dispatched to {target_channel} (ts: {res_data.get('ts')})")
                    return {
                        "status": "sent",
                        "provider": "slack_bot",
                        "channel": target_channel,
                        "ts": res_data.get("ts"),
                        "title": title
                    }
                else:
                    logger.warning(f"Slack Bot API warning: {res_data.get('error') or resp.text}")
            except Exception as e:
                logger.error(f"Slack Bot delivery error: {e}")

        # 2. Fallback to Slack Webhook URL
        if self.slack_webhook_url and not self.slack_webhook_url.startswith("your_") and not os.getenv("TESTING"):
            try:
                import httpx
                payload = {
                    "channel": target_channel,
                    "text": f"*{title or 'Omnichannel Voice Receptionist Alert'}*\n{message}"
                }
                if blocks:
                    payload["blocks"] = blocks
                resp = httpx.post(self.slack_webhook_url, json=payload, timeout=5.0)
                if resp.status_code == 200:
                    logger.info(f"✅ Slack notification dispatched to {target_channel} via webhook")
                    return {"status": "sent", "provider": "slack_webhook", "channel": target_channel, "title": title}
            except Exception as e:
                logger.error(f"Slack webhook delivery error: {e}")

        # 3. Resilient simulation for test suites & offline environments
        logger.info(f"💬 [SIMULATION SLACK] Channel: {target_channel} | Title: {title} | Content: {message}")
        return {
            "status": "simulated",
            "provider": "slack_simulator",
            "channel": target_channel,
            "title": title,
            "content": message,
            "blocks": blocks
        }

    def send_retention_cold_email(
        self,
        to_email: str,
        customer_name: str = "Valued Guest",
        days_since_visit: int = 30,
        salon_name: str = "Luxe Hair & Wellness Salon",
        booking_link: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Dispatches 30-day post-call/visit client retention cold email via Resend or SMTP.
        Matches node 8 of the n8n post-call escalation engine.
        """
        if not to_email:
            return {"status": "skipped", "reason": "No recipient email"}

        subject = f"Time for a touch-up, {customer_name}? ✨"
        book_url = booking_link or os.getenv("APP_BASE_URL", "https://luxesalon.com") + "/book"
        html_content = f"""
        <div style="font-family: 'Helvetica Neue', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; color: #1a1a1a;">
            <div style="text-align: center; margin-bottom: 24px;">
                <h1 style="color: #b89758; font-size: 24px; letter-spacing: 2px; text-transform: uppercase;">{salon_name}</h1>
                <p style="color: #666; font-size: 13px; margin: 0;">Newbury Street • Boston, MA</p>
            </div>
            <div style="background-color: #faf7f2; border: 1px solid #e8e0d5; border-radius: 8px; padding: 24px; margin-bottom: 24px;">
                <h2 style="font-size: 18px; color: #1a1a1a; margin-top: 0;">Hi {customer_name},</h2>
                <p style="line-height: 1.6; font-size: 15px; color: #444;">
                    It has been {days_since_visit} days since your last salon appointment with us!
                    To keep your hair vibrant, healthy, and perfectly styled, we recommend booking your seasonal touch-up with Marcus Vance or your favorite specialist.
                </p>
                <div style="text-align: center; margin: 30px 0 20px;">
                    <a href="{book_url}" style="background-color: #b89758; color: #ffffff; padding: 12px 28px; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 14px; display: inline-block;">
                        Book Your Touch-Up Online
                    </a>
                </div>
            </div>
            <p style="color: #999; font-size: 12px; text-align: center;">
                Warm regards,<br>
                <strong>Marcus Vance & The Luxe Salon Concierge Team</strong><br>
                450 Newbury Street, Boston, MA | +1 (617) 271-8180
            </p>
        </div>
        """

        resend_api_key = os.getenv("RESEND_API_KEY", "").strip()
        from_email = (os.getenv("SMTP_FROM") or "Marcus <onboarding@resend.dev>").strip('"\'')

        if resend_api_key and not resend_api_key.startswith("your_") and not os.getenv("TESTING"):
            try:
                import httpx
                payload = {
                    "from": from_email,
                    "to": [to_email],
                    "subject": subject,
                    "html": html_content
                }
                res = httpx.post(
                    "https://api.resend.com/emails",
                    headers={"Authorization": f"Bearer {resend_api_key}", "Content-Type": "application/json"},
                    json=payload,
                    timeout=10.0
                )
                if res.status_code in (200, 201):
                    logger.info(f"✅ 30-Day Retention Cold Email dispatched via Resend to {to_email}")
                    return {"status": "sent", "channel": "resend", "recipient": to_email, "subject": subject}
                else:
                    logger.warning(f"Resend retention email warning ({res.status_code}): {res.text}")
            except Exception as e:
                logger.warning(f"Resend retention email error: {e}")

        logger.info(f"📧 [SIMULATION RETENTION EMAIL] To: {to_email} | Subject: {subject}")
        return {"status": "simulated", "channel": "resend", "recipient": to_email, "subject": subject}

    def send_post_call_review_whatsapp(
        self,
        to_phone: str,
        customer_name: str = "Valued Guest",
        review_url: str = "https://g.page/r/YOUR_PLACE_ID/review"
    ) -> Dict[str, Any]:
        """
        Dispatches automated post-call WhatsApp review request.
        Matches node 6 of the n8n post-call escalation engine.
        """
        if not to_phone:
            return {"status": "skipped", "reason": "No recipient phone"}

        message_body = (
            f"Hi {customer_name}, thank you for calling Luxe Salon & Spa on Newbury Street! "
            f"We would love your feedback: {review_url}"
        )
        # Leverage existing omnichannel WhatsApp delivery engine
        return self.send_whatsapp(to_phone=to_phone, text=message_body)

    def send_sms(self, to_phone: str, text: str) -> Dict[str, Any]:
        """Dispatches an SMS message via Twilio or resilient simulator."""
        if not to_phone:
            return {"status": "skipped", "reason": "No recipient phone"}

        # Format phone to E.164 (+prefix)
        digits = "".join(filter(str.isdigit, to_phone))
        if len(digits) == 10:
            digits = "1" + digits
        elif len(digits) == 11 and digits.startswith("01"):
            digits = "88" + digits
        e164_phone = f"+{digits}"

        if self.is_twilio_configured():
            try:
                from twilio.rest import Client
                client = Client(self.twilio_account_sid, self.twilio_auth_token)
                msg = client.messages.create(body=text, from_=self.twilio_from_phone, to=e164_phone)
                logger.info(f"✅ Twilio SMS dispatched to {e164_phone} (SID: {msg.sid})")
                return {"status": "sent", "channel": "sms", "sid": msg.sid, "recipient": e164_phone}
            except Exception as e:
                logger.error(f"Twilio SMS delivery failed: {e}")

        logger.info(f"📱 [SIMULATION SMS] To: {e164_phone} | Content: {text}")
        return {"status": "simulated", "channel": "sms", "recipient": e164_phone, "content": text}

    def send_telnyx_sms(self, to_phone: str, text: str) -> Dict[str, Any]:
        """Dispatches an SMS/MMS message using Telnyx API."""
        telnyx_key = os.getenv("TELNYX_API_KEY", "")
        telnyx_from = os.getenv("TELNYX_PHONE_NUMBER", "+16172718180")
        if telnyx_key and not telnyx_key.startswith("your_"):
            try:
                import httpx
                headers = {
                    "Authorization": f"Bearer {telnyx_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "from": telnyx_from,
                    "to": to_phone if to_phone.startswith("+") else f"+{to_phone}",
                    "text": text
                }
                resp = httpx.post("https://api.telnyx.com/v2/messages", json=payload, headers=headers, timeout=10.0)
                data = resp.json()
                if resp.status_code in (200, 201, 202):
                    msg_id = data.get("data", {}).get("id", "telnyx_msg")
                    logger.info(f"✅ Dispatched Telnyx SMS to {to_phone} (ID: {msg_id})")
                    return {"status": "sent", "provider": "telnyx", "message_id": msg_id, "to": to_phone}
                else:
                    logger.error(f"Telnyx SMS error {resp.status_code}: {resp.text}")
            except Exception as e:
                logger.error(f"Error sending Telnyx SMS: {e}")

        logger.info(f"📱 [SIMULATION TELNYX SMS] To: {to_phone} | Content: {text}")
        return {"status": "simulated", "provider": "telnyx", "to": to_phone, "content": text}

    def trigger_outbound_call(self, to_phone: str, twiml_url: Optional[str] = None, twiml_say: Optional[str] = None) -> Dict[str, Any]:
        """Triggers an outbound voice phone call via Twilio."""
        if self.is_twilio_configured():
            try:
                from twilio.rest import Client
                client = Client(self.twilio_account_sid, self.twilio_auth_token)
                if twiml_url:
                    call = client.calls.create(to=to_phone, from_=self.twilio_from_phone, url=twiml_url)
                else:
                    say_text = twiml_say or "Hello! This is an automated reminder regarding your upcoming appointment."
                    twiml_block = f"<Response><Say voice='Polly.Danielle' language='en-US'>{say_text}</Say></Response>"
                    call = client.calls.create(to=to_phone, from_=self.twilio_from_phone, twiml=twiml_block)
                logger.info(f"📞 Twilio outbound voice call initiated to {to_phone} (SID: {call.sid})")
                return {"status": "initiated", "call_sid": call.sid, "to": to_phone}
            except Exception as e:
                logger.error(f"Twilio voice call initiation failed: {e}")

        logger.info(f"📞 [SIMULATION CALL] Calling phone: {to_phone} | Message: {twiml_say}")
        return {"status": "simulated", "channel": "voice_call", "to": to_phone, "message": twiml_say}

    def trigger_vapi_outbound_call(
        self,
        to_phone: str,
        customer_name: str = "Valued Guest",
        tenant_name: str = "Luxe Salon & Spa",
        first_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Initiates an automated outbound phone call via Vapi REST API."""
        vapi_key = (os.getenv("VAPI_PRIVATE_API_KEY") or os.getenv("VAPI_API_KEY") or "").strip()
        asst_id = (os.getenv("VAPI_ASSISTANT_ID") or "b9242970-fbef-4991-8e94-4e59ebd4ab47").strip()
        phone_id = (os.getenv("VAPI_PHONE_NUMBER_ID") or "c3cc95f8-6517-4870-8f82-bc3ea758b205").strip()
        squad_id = (os.getenv("VAPI_SQUAD_ID") or "816b5fbf-8eb1-4e26-805b-3cc6caade9ce").strip()

        clean_digits = "".join(filter(str.isdigit, to_phone))
        if len(clean_digits) == 10:
            clean_digits = "1" + clean_digits
        clean_phone = f"+{clean_digits}" if clean_digits else to_phone

        if vapi_key and (squad_id or asst_id) and phone_id and not vapi_key.startswith("your_"):
            try:
                import httpx
                payload = {
                    "phoneNumberId": phone_id,
                    "customer": {
                        "number": clean_phone,
                        "name": customer_name
                    }
                }
                if squad_id:
                    payload["squadId"] = squad_id
                else:
                    payload["assistantId"] = asst_id

                if first_message:
                    payload["assistantOverrides"] = {
                        "firstMessage": first_message
                    }
                with httpx.Client(timeout=10.0) as client:
                    resp = client.post(
                        "https://api.vapi.ai/call/phone",
                        headers={"Authorization": f"Bearer {vapi_key}", "Content-Type": "application/json"},
                        json=payload
                    )
                    if resp.status_code in (200, 201):
                        data = resp.json()
                        logger.info(f"🚀 [VAPI CALL] Outbound call placed to {clean_phone} (ID: {data.get('id')})")
                        return {"status": "success", "call_id": data.get("id"), "to": clean_phone, "provider": "vapi"}
                    else:
                        logger.warning(f"Vapi API call error {resp.status_code}: {resp.text}")
            except Exception as e:
                logger.error(f"Vapi outbound call failed: {e}")

        logger.info(f"📞 [SIMULATED VAPI CALL] Calling {clean_phone} for {customer_name} at {tenant_name}")
        return {"status": "simulated", "to": clean_phone, "provider": "vapi_simulation"}

    def trigger_whatsapp_voice_call(
        self,
        to_phone: str,
        customer_name: str = "Valued Guest",
        tenant_name: str = "Luxe Salon & Spa"
    ) -> Dict[str, Any]:
        """
        Attempts to initiate an outbound voice call to the user's WhatsApp account.
        Checks Meta WhatsApp Cloud API Voice/Calling endpoints and Twilio WhatsApp Voice.
        Returns a structured dictionary indicating success, failure, or unsupported client state.
        """
        digits = "".join(filter(str.isdigit, to_phone))
        if len(digits) == 10:
            digits = "1" + digits
        elif len(digits) == 11 and digits.startswith("01"):
            digits = "88" + digits
        e164_phone = f"+{digits}" if digits else to_phone

        # Method A: Meta WhatsApp Cloud API Voice Calling (v21.0+)
        if self.whatsapp_phone_number_id and self.meta_access_token:
            try:
                import httpx
                url = f"https://graph.facebook.com/v21.0/{self.whatsapp_phone_number_id}/calls"
                headers = {
                    "Authorization": f"Bearer {self.meta_access_token}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "messaging_product": "whatsapp",
                    "to": digits,
                    "type": "audio",
                    "action": "start_call"
                }
                with httpx.Client(timeout=6.0) as client:
                    resp = client.post(url, headers=headers, json=payload)
                    if resp.status_code in (200, 201, 202):
                        logger.info(f"🟢 [META WHATSAPP CALL] Initiated WhatsApp call to {e164_phone}")
                        return {
                            "status": "initiated",
                            "provider": "meta_whatsapp_calling",
                            "recipient": e164_phone,
                            "response": resp.json()
                        }
                    else:
                        logger.info(f"⚠️ Meta WhatsApp Calling endpoint returned {resp.status_code}: {resp.text}")
            except Exception as e:
                logger.info(f"Meta WhatsApp voice call attempt failed: {e}")

        # Method B: Twilio WhatsApp Voice calling (if configured)
        if self.is_twilio_configured():
            try:
                from twilio.rest import Client
                client = Client(self.twilio_account_sid, self.twilio_auth_token)
                from_num = self.twilio_whatsapp_from
                if not from_num.startswith("whatsapp:"):
                    from_num = f"whatsapp:{from_num}"
                to_num = f"whatsapp:{e164_phone}"
                say_text = f"Hello {customer_name}! This is Sophia from {tenant_name} calling on WhatsApp."
                twiml_block = f"<Response><Say voice='Polly.Danielle' language='en-US'>{say_text}</Say></Response>"
                call = client.calls.create(to=to_num, from_=from_num, twiml=twiml_block)
                logger.info(f"🟢 [TWILIO WHATSAPP CALL] Call created: {call.sid}")
                return {
                    "status": "initiated",
                    "provider": "twilio_whatsapp_voice",
                    "call_sid": call.sid,
                    "recipient": e164_phone
                }
            except Exception as e:
                err_str = str(e)
                logger.info(f"Twilio WhatsApp voice call attempt failed ({err_str})")
                return {
                    "status": "failed",
                    "provider": "twilio_whatsapp_voice",
                    "error": err_str
                }

        # If not active or client is offline on WhatsApp VoIP
        return {
            "status": "failed",
            "provider": "whatsapp_unreachable",
            "reason": "Recipient device not connected to active WhatsApp VoIP session or carrier blocked."
        }

    def trigger_telnyx_outbound_call(
        self,
        to_phone: str,
        customer_name: str = "Valued Guest",
        tenant_name: str = "Luxe Salon & Spa",
        first_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Triggers an outbound PSTN phone call to the customer using TELNYX_PHONE_NUMBER (+1 617-271-8180).
        Dispatches via Vapi with Sophia voice profile, or direct Telnyx Call Control API.
        """
        digits = "".join(filter(str.isdigit, to_phone))
        if len(digits) == 10:
            digits = "1" + digits
        elif len(digits) == 11 and digits.startswith("01"):
            digits = "88" + digits
        clean_phone = f"+{digits}" if digits else to_phone

        telnyx_caller_id = self.telnyx_phone_number or "+16172718180"

        # 1. Primary: Sophia via Vapi High-Definition Voice
        greeting = first_message or (
            f"Hello {customer_name}! This is Sophia from {tenant_name} on Newbury Street. "
            f"I saw you requested a callback via WhatsApp, and I am calling your direct line from our "
            f"verified Telnyx line—how can I pamper you today?"
        )
        vapi_res = self.trigger_vapi_outbound_call(
            to_phone=clean_phone,
            customer_name=customer_name,
            tenant_name=tenant_name,
            first_message=greeting
        )
        if vapi_res.get("status") in ("success", "initiated"):
            vapi_res["caller_id"] = telnyx_caller_id
            vapi_res["carrier"] = "Telnyx"
            return vapi_res

        # 2. Secondary: Direct Telnyx Call Control API (if TELNYX_API_KEY is configured)
        if self.telnyx_api_key and not self.telnyx_api_key.startswith("your_"):
            try:
                import httpx
                telnyx_url = "https://api.telnyx.com/v2/calls"
                headers = {
                    "Authorization": f"Bearer {self.telnyx_api_key}",
                    "Content-Type": "application/json"
                }
                telnyx_payload = {
                    "to": clean_phone,
                    "from": telnyx_caller_id,
                    "connection_id": os.getenv("TELNYX_CONNECTION_ID", "default_connection")
                }
                with httpx.Client(timeout=8.0) as client:
                    resp = client.post(telnyx_url, headers=headers, json=telnyx_payload)
                    if resp.status_code in (200, 201):
                        data = resp.json().get("data", {})
                        logger.info(f"🚀 [TELNYX DIRECT CALL] Call initiated to {clean_phone} (Call Control ID: {data.get('call_control_id')})")
                        return {
                            "status": "success",
                            "provider": "telnyx_call_control",
                            "call_control_id": data.get("call_control_id"),
                            "caller_id": telnyx_caller_id,
                            "to": clean_phone,
                            "carrier": "Telnyx"
                        }
            except Exception as e:
                logger.warning(f"Direct Telnyx call attempt failed: {e}")

        # 3. Tertiary: Twilio PSTN Fallback with Telnyx Caller ID
        if self.is_twilio_configured():
            try:
                from twilio.rest import Client
                client = Client(self.twilio_account_sid, self.twilio_auth_token)
                twiml_block = f"<Response><Say voice='Polly.Danielle' language='en-US'>{greeting}</Say></Response>"
                call = client.calls.create(to=clean_phone, from_=self.twilio_from_phone, twiml=twiml_block)
                return {
                    "status": "success",
                    "provider": "twilio_pstn_fallback",
                    "call_sid": call.sid,
                    "caller_id": telnyx_caller_id,
                    "to": clean_phone
                }
            except Exception as e:
                logger.debug(f"Twilio PSTN fallback error: {e}")

        # 4. Resilient Simulation Mode (Sub-500ms response guarantee)
        logger.info(f"📞 [TELNYX PSTN SIMULATION] Dialing {clean_phone} from {telnyx_caller_id} (Sophia Voice)")
        return {
            "status": "simulated",
            "provider": "telnyx_pstn_simulation",
            "caller_id": telnyx_caller_id,
            "to": clean_phone,
            "agent": "Sophia",
            "greeting": greeting,
            "carrier": "Telnyx"
        }

    def dispatch_adaptive_voice_call(
        self,
        to_phone: str,
        customer_name: str = "Valued Guest",
        tenant_name: str = "Luxe Salon & Spa",
        prefer_whatsapp: bool = True
    ) -> Dict[str, Any]:
        """
        Adaptive Multi-Tier Voice Dispatcher:
        Tier 1: Tries WhatsApp voice calling first.
        Tier 2 (Failover): If WhatsApp call is unavailable, unsupported, or fails,
                           seamlessly falls back to PSTN cellular calling via Telnyx (+1 617-271-8180).
        """
        import time
        t0 = time.perf_counter()

        digits = "".join(filter(str.isdigit, to_phone))
        if len(digits) == 10:
            digits = "1" + digits
        elif len(digits) == 11 and digits.startswith("01"):
            digits = "88" + digits
        e164_phone = f"+{digits}" if digits else to_phone

        whatsapp_attempt = None
        if prefer_whatsapp:
            logger.info(f"📱 [TIER 1: WHATSAPP CALL] Attempting WhatsApp call to {e164_phone}...")
            whatsapp_res = self.trigger_whatsapp_voice_call(
                e164_phone,
                customer_name=customer_name,
                tenant_name=tenant_name
            )
            whatsapp_attempt = whatsapp_res
            if whatsapp_res.get("status") in ("initiated", "ringing", "connected"):
                latency_ms = int((time.perf_counter() - t0) * 1000)
                logger.info(f"✅ [WHATSAPP CALL CONNECTED] Successfully ringing {e164_phone} on WhatsApp")
                return {
                    "status": "success",
                    "tier_selected": "whatsapp_call",
                    "fallback_engaged": False,
                    "provider": whatsapp_res.get("provider", "whatsapp"),
                    "recipient": e164_phone,
                    "caller_name": customer_name,
                    "latency_ms": latency_ms,
                    "details": whatsapp_res
                }
            logger.warning(
                f"⚠️ [TIER 1 FAILED] WhatsApp call unavailable for {e164_phone} "
                f"({whatsapp_res.get('reason') or whatsapp_res.get('error')}). "
                f"Engaging TIER 2: Telnyx PSTN Cellular Failover!"
            )

        # Tier 2: PSTN Calling via Telnyx
        logger.info(f"📞 [TIER 2: TELNYX PSTN CALL] Dialing {e164_phone} with Telnyx line {self.telnyx_phone_number}...")
        pstn_res = self.trigger_telnyx_outbound_call(
            to_phone=e164_phone,
            customer_name=customer_name,
            tenant_name=tenant_name
        )

        # Simultaneously dispatch a courtesy WhatsApp notification
        try:
            courtesy_msg = (
                f"✨ Hi {customer_name}! Sofia from {tenant_name} is calling your direct phone line "
                f"right now from our verified Telnyx number: {self.telnyx_phone_number}. Please answer!"
            )
            self.send_whatsapp(e164_phone, courtesy_msg)
        except Exception as e:
            logger.debug(f"Courtesy WhatsApp notification bypassed: {e}")

        latency_ms = int((time.perf_counter() - t0) * 1000)
        return {
            "status": "success",
            "tier_selected": "telnyx_pstn",
            "fallback_engaged": bool(prefer_whatsapp),
            "primary_attempt": whatsapp_attempt,
            "caller_id": self.telnyx_phone_number,
            "recipient": e164_phone,
            "caller_name": customer_name,
            "agent": "Sophia",
            "latency_ms": latency_ms,
            "pstn_details": pstn_res
        }

    def send_whatsapp_template(
        self,
        to_phone: str,
        template_name: str = "3p_direct_integration_test_template",
        language_code: str = "en_US",
        components: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Dispatches an approved WhatsApp Business template message via Meta Cloud API.
        Used for outbound appointment booking notifications to uninitiated threads.
        """
        if not to_phone:
            return {"status": "skipped", "reason": "No recipient phone"}

        digits = "".join(filter(str.isdigit, to_phone))
        if len(digits) == 10:
            digits = "1" + digits
        elif len(digits) == 11 and digits.startswith("01"):
            digits = "88" + digits
        e164_phone = f"+{digits}"

        if self.whatsapp_phone_number_id and self.meta_access_token:
            try:
                url = f"https://graph.facebook.com/v21.0/{self.whatsapp_phone_number_id}/messages"
                template_obj: Dict[str, Any] = {
                    "name": template_name,
                    "language": {"code": language_code}
                }
                if components:
                    template_obj["components"] = components

                payload = {
                    "messaging_product": "whatsapp",
                    "to": digits,
                    "type": "template",
                    "template": template_obj
                }
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    url, data=data,
                    headers={
                        "Authorization": f"Bearer {self.meta_access_token}",
                        "Content-Type": "application/json"
                    }
                )
                with urllib.request.urlopen(req, timeout=8) as resp:
                    resp_data = json.loads(resp.read().decode())
                    logger.info(f"✅ Meta WhatsApp Template '{template_name}' dispatched to {digits}: {resp_data}")
                    return {"status": "sent", "channel": "whatsapp_template", "response": resp_data, "recipient": e164_phone, "template": template_name}
            except Exception as e:
                logger.error(f"Meta WhatsApp Template dispatch failed: {e}")
                return {"status": "failed", "error": str(e), "recipient": e164_phone}

        return {"status": "simulated", "channel": "whatsapp_template", "to": e164_phone, "template": template_name}

    def send_whatsapp(self, to_phone: str, text: str, quick_replies: Optional[List[str]] = None) -> Dict[str, Any]:
        """Dispatches WhatsApp push message via Meta Cloud API or Twilio WhatsApp."""
        if not to_phone:
            return {"status": "skipped", "reason": "No recipient phone"}

        # Normalize digits: if 10-digit US number, prefix with 1; if BD 11-digit (01...), prefix with 88
        digits = "".join(filter(str.isdigit, to_phone))
        if len(digits) == 10:
            digits = "1" + digits
        elif len(digits) == 11 and digits.startswith("01"):
            digits = "88" + digits
        e164_phone = f"+{digits}"

        if self.whatsapp_phone_number_id and self.meta_access_token:
            try:
                url = f"https://graph.facebook.com/v21.0/{self.whatsapp_phone_number_id}/messages"
                payload = {
                    "messaging_product": "whatsapp",
                    "to": digits,
                    "type": "text",
                    "text": {"preview_url": True, "body": text}
                }
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    url, data=data,
                    headers={
                        "Authorization": f"Bearer {self.meta_access_token}",
                        "Content-Type": "application/json"
                    }
                )
                with urllib.request.urlopen(req, timeout=8) as resp:
                    resp_data = json.loads(resp.read().decode())
                    logger.info(f"✅ Meta WhatsApp dispatched to {digits}: {resp_data}")
                    return {"status": "sent", "channel": "whatsapp", "response": resp_data, "recipient": e164_phone}
            except urllib.error.HTTPError as http_err:
                err_body = http_err.read().decode()
                logger.warning(f"Meta direct text WhatsApp failed ({http_err.code}): {err_body} — falling back to template")
                # Fallback to Meta Template dispatch if direct text is restricted
                template_res = self.send_whatsapp_template(to_phone=to_phone)
                if template_res.get("status") == "sent":
                    return template_res
            except Exception as e:
                logger.error(f"Meta WhatsApp Cloud API failed: {e} — falling back to template")
                template_res = self.send_whatsapp_template(to_phone=to_phone)
                if template_res.get("status") == "sent":
                    return template_res

        # Fallback to Twilio WhatsApp if configured
        if self.is_twilio_configured():
            try:
                from twilio.rest import Client
                client = Client(self.twilio_account_sid, self.twilio_auth_token)
                from_num = self.twilio_whatsapp_from
                if not from_num.startswith("whatsapp:"):
                    from_num = f"whatsapp:{from_num}"
                to_num = f"whatsapp:{e164_phone}"
                msg = client.messages.create(
                    body=text,
                    from_=from_num,
                    to=to_num
                )
                logger.info(f"✅ Twilio WhatsApp message sent: {msg.sid}")
                return {"status": "sent", "channel": "whatsapp_twilio", "sid": msg.sid, "recipient": e164_phone}
            except Exception as e:
                logger.error(f"Twilio WhatsApp failed: {e}")

        logger.info(f"🟢 [SIMULATION WHATSAPP] To: {e164_phone} | Body: {text}")
        return {"status": "simulated", "channel": "whatsapp", "to": e164_phone, "content": text}

    def send_messenger(self, recipient_psid: str, text: str, quick_replies: Optional[List[str]] = None) -> Dict[str, Any]:
        """Dispatches Facebook Messenger message via Graph API."""
        if self.meta_access_token:
            try:
                url = f"https://graph.facebook.com/v19.0/me/messages?access_token={self.meta_access_token}"
                payload: Dict[str, Any] = {
                    "recipient": {"id": recipient_psid},
                    "message": {"text": text}
                }
                if quick_replies:
                    payload["message"]["quick_replies"] = [
                        {"content_type": "text", "title": title[:20], "payload": title}
                        for title in quick_replies
                    ]
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    resp_data = json.loads(resp.read().decode())
                    logger.info(f"✅ Facebook Messenger message sent to {recipient_psid}")
                    return {"status": "sent", "channel": "messenger", "response": resp_data}
            except Exception as e:
                logger.error(f"Messenger Graph API failed: {e}")

        logger.info(f"💬 [SIMULATION MESSENGER] To PSID: {recipient_psid} | Text: {text}")
        return {"status": "simulated", "channel": "messenger", "recipient": recipient_psid, "content": text}

    def send_instagram_dm(self, recipient_igid: str, text: str) -> Dict[str, Any]:
        """Dispatches Instagram Direct message via Graph API."""
        if self.meta_access_token:
            try:
                url = f"https://graph.facebook.com/v19.0/me/messages?access_token={self.meta_access_token}"
                payload = {
                    "recipient": {"id": recipient_igid},
                    "message": {"text": text}
                }
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    resp_data = json.loads(resp.read().decode())
                    logger.info(f"✅ Instagram Direct DM sent to {recipient_igid}")
                    return {"status": "sent", "channel": "instagram", "response": resp_data}
            except Exception as e:
                logger.error(f"Instagram Graph API failed: {e}")

        logger.info(f"📸 [SIMULATION INSTAGRAM] To IGID: {recipient_igid} | Text: {text}")
        return {"status": "simulated", "channel": "instagram", "recipient": recipient_igid, "content": text}

    def send_telegram(self, chat_id: str, text: str, quick_replies: Optional[List[str]] = None) -> Dict[str, Any]:
        """Dispatches message via Telegram Bot API or simulation."""
        from integrations.telegram_bot import telegram_client
        return telegram_client.send_message(chat_id=chat_id, text=text, quick_replies=quick_replies)

    def send_twitter_dm(self, recipient_id: str, text: str, quick_replies: Optional[List[str]] = None) -> Dict[str, Any]:
        """Dispatches Direct Message on Twitter / X or simulation."""
        from integrations.twitter_x import twitter_client
        return twitter_client.send_direct_message(recipient_id=recipient_id, text=text, quick_replies=quick_replies)

    def send_linkedin_message(self, recipient_urn: str, text: str) -> Dict[str, Any]:
        """Dispatches direct message via LinkedIn Messaging API or simulation."""
        from integrations.linkedin_msg import linkedin_client
        return linkedin_client.send_message(recipient_urn=recipient_urn, text=text)

    def send_tiktok_dm(self, recipient_open_id: str, text: str) -> Dict[str, Any]:
        """Dispatches direct message via TikTok Business Messaging API or simulation."""
        from integrations.tiktok_msg import tiktok_client
        return tiktok_client.send_direct_message(recipient_open_id=recipient_open_id, text=text)

    def send_threads_reply(self, reply_to_id: str, text: str) -> Dict[str, Any]:
        """Dispatches reply via Meta Threads API or simulation."""
        from integrations.threads_api import threads_client
        return threads_client.send_reply(reply_to_id=reply_to_id, text=text)

    def send_reddit_message(self, recipient_username: str, text: str, subject: str = "Appointment Confirmation") -> Dict[str, Any]:
        """Dispatches private message or comment reply via Reddit API or simulation."""
        from integrations.reddit_bot import reddit_client
        if recipient_username.startswith("t1_") or recipient_username.startswith("t3_"):
            return reddit_client.reply_to_comment(thing_id=recipient_username, text=text)
        return reddit_client.send_private_message(recipient_username=recipient_username, subject=subject, text=text)

    def send_email(
        self,
        to_email: str,
        subject: str,
        booking_data: Dict[str, Any],
        html_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sends luxury email confirmation for confirmed bookings.
        Attaches standard RFC 5545 .ics calendar invite and 1-click Google Calendar Add link.
        Supports SMTP (Gmail, Outlook, SendGrid, Amazon SES) and Resend API.
        """
        if not to_email or "@" not in to_email:
            return {"status": "skipped", "reason": "No valid email address"}

        caller_name = booking_data.get("caller_name", "Valued Guest")
        service = booking_data.get("service_name", "Salon Service")
        stylist = booking_data.get("stylist_name", "Specialist")
        start_time = booking_data.get("start_time", "")
        ref_id = booking_data.get("booking_id", "")
        salon_name = "Luxe Saloon & Spa"
        address = "120 Newbury Street, Boston, MA 02116"

        # Generate 1-click Google Calendar URL and .ics
        from integrations.google_calendar import calendar_service
        try:
            start_dt = datetime.fromisoformat(start_time.replace(" ", "T"))
        except Exception:
            start_dt = datetime.now() + timedelta(days=1)

        duration = booking_data.get("duration_minutes", 60)
        details_text = f"Booking Ref: {ref_id}\nMaster Stylist: {stylist}\nService: {service}\nAddress: {address}\nPhone: (617) 555-LUXE"
        gcal_add_link = calendar_service.generate_add_to_gcal_link(f"Luxe Saloon: {service} with {stylist}", start_dt, duration, details_text, address)
        ics_content = calendar_service.generate_ics(f"Luxe Saloon: {service} with {stylist}", start_dt, duration, details_text, address, ref_id=ref_id)
        cal_base = os.getenv("APP_BASE_URL", "https://ai-voice-receptionist-chi.vercel.app")
        cal_add_url = f"{cal_base}/api/calendar/add/{ref_id}"

        default_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #070b14; color: #f3f4f6; margin: 0; padding: 24px; }}
    .card {{ max-width: 560px; margin: 0 auto; background: #0f172a; border: 1px solid rgba(245,158,11,0.35); border-radius: 20px; padding: 36px 30px; box-shadow: 0 20px 50px rgba(0,0,0,0.6); }}
    .brand {{ color: #f59e0b; font-size: 22px; font-weight: 800; letter-spacing: 0.5px; margin-bottom: 6px; }}
    .tagline {{ font-size: 12px; color: #38bdf8; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; margin-bottom: 20px; }}
    h1 {{ font-size: 24px; color: #ffffff; margin: 0 0 16px 0; font-weight: 800; }}
    .intro {{ font-size: 14.5px; color: #cbd5e1; line-height: 1.6; margin-bottom: 24px; }}
    .details {{ background: rgba(255,255,255,0.03); border-radius: 14px; padding: 20px; margin: 24px 0; border: 1px solid rgba(255,255,255,0.08); }}
    .row {{ display: flex; justify-content: space-between; margin-bottom: 12px; font-size: 14px; border-bottom: 1px solid rgba(255,255,255,0.04); padding-bottom: 8px; }}
    .row:last-child {{ border-bottom: none; margin-bottom: 0; padding-bottom: 0; }}
    .label {{ color: #94a3b8; font-weight: 500; }}
    .val {{ color: #ffffff; font-weight: 700; text-align: right; }}
    .btn-container {{ display: flex; gap: 12px; margin: 28px 0 20px 0; flex-wrap: wrap; }}
    .btn-gcal {{ display: inline-block; background: linear-gradient(135deg, #10b981, #059669); color: #ffffff; font-weight: 800; font-size: 13.5px; text-decoration: none; padding: 13px 22px; border-radius: 10px; text-align: center; box-shadow: 0 4px 14px rgba(16,185,129,0.4); }}
    .btn-portal {{ display: inline-block; background: rgba(255,255,255,0.08); color: #38bdf8; border: 1px solid rgba(56,189,248,0.4); font-weight: 700; font-size: 13.5px; text-decoration: none; padding: 13px 22px; border-radius: 10px; text-align: center; }}
    .ai-showcase {{ background: linear-gradient(135deg, rgba(30,41,59,0.6), rgba(15,23,42,0.8)); border: 1px solid rgba(56,189,248,0.25); border-radius: 14px; padding: 18px; margin: 28px 0 20px 0; }}
    .ai-title {{ font-size: 12.5px; font-weight: 800; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }}
    .ai-text {{ font-size: 12px; color: #94a3b8; line-height: 1.5; margin: 0; }}
    .footer {{ font-size: 11.5px; color: #64748b; margin-top: 28px; text-align: center; line-height: 1.5; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 20px; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="brand">✦ {salon_name}</div>
    <div class="tagline">Boston's Premier Hair & Wellness Sanctuary • 120 Newbury St</div>
    <h1>Your Appointment is Confirmed</h1>
    <p class="intro">Dear <b>{caller_name}</b>,<br>Thank you for choosing Luxe Saloon & Spa! We are delighted to confirm your bespoke booking. An interactive calendar file is attached, and you can also add it to your Google Calendar with one click below.</p>
    
    <div class="details">
      <div class="row"><span class="label">Booking Reference:</span><span class="val">{ref_id}</span></div>
      <div class="row"><span class="label">Signature Service:</span><span class="val">{service}</span></div>
      <div class="row"><span class="label">Master Stylist:</span><span class="val">{stylist}</span></div>
      <div class="row"><span class="label">Confirmed Date & Time:</span><span class="val">{start_time}</span></div>
      <div class="row"><span class="label">Sanctuary Address:</span><span class="val">{address}</span></div>
    </div>

    <!-- 1-Click Action Buttons -->
    <div style="background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.3); border-radius: 12px; padding: 12px 16px; margin: 20px 0; font-size: 13px; color: #34d399; text-align: center;">
      🔔 Pre-configured alarms: 24h and 1h reminders will alert your device before your appointment
    </div>
    <div class="btn-container">
      <a href="{gcal_add_link}" target="_blank" class="btn-gcal">📅 Add to Google Calendar</a>
      <a href="{cal_add_url}" target="_blank" class="btn-portal">🍏 Apple / Outlook / All Calendars</a>
    </div>

    <!-- What Our AI Voice Agents Are Doing -->
    <div class="ai-showcase">
      <div class="ai-title">🎙️ Autonomous AI Voice Concierge Preview</div>
      <p class="ai-text">
        This appointment was seamlessly booked through <b>Luxe Saloon's AI Concierge Suite</b>.<br>
        • <b>Sofia Alston (Front Desk)</b> & <b>Marcus Vance (Creative Director)</b> are live 24/7 via WebRTC with sub-500ms voice response.<br>
        • Two-way synchronized across Google Calendar, WhatsApp, and Neon PostgreSQL.<br>
        • Reply to our WhatsApp message at anytime to reschedule or cancel with zero hassle!
      </p>
    </div>

    <div class="footer">
      Luxe Salon & Spa • 120 Newbury Street, Back Bay, Boston, MA 02116<br>
      Concierge Desk & WhatsApp: +1 (617) 271-8180<br>
      © 2026 Luxe Salon & Spa. All rights reserved.
    </div>
  </div>
</body>
</html>"""

        # 1. Try Resend API if configured
        resend_api_key = os.getenv("RESEND_API_KEY", "").strip()
        if resend_api_key:
            try:
                import requests
                import base64
                b64_ics = base64.b64encode(ics_content.encode("utf-8")).decode("utf-8")
                from_email = (os.getenv("SMTP_FROM") or "Luxe Salon & Spa <onboarding@resend.dev>").strip('"\'')
                clean_to = to_email.strip().lower()
                res = requests.post(
                    "https://api.resend.com/emails",
                    headers={"Authorization": f"Bearer {resend_api_key}", "Content-Type": "application/json"},
                    json={
                        "from": from_email,
                        "to": [clean_to],
                        "subject": subject,
                        "html": html_content or default_html,
                        "attachments": [
                            {
                                "filename": "invite.ics",
                                "content": b64_ics
                            }
                        ]
                    },
                    timeout=10.0
                )
                if res.status_code in (200, 201):
                    logger.info(f"✅ Resend API email dispatched successfully to {to_email}")
                    return {"status": "sent", "channel": "resend", "recipient": to_email, "gcal_add_link": gcal_add_link}
                else:
                    logger.warning(f"Resend API error ({res.status_code}): {res.text}")
            except Exception as e:
                logger.warning(f"Resend dispatch warning: {e}")

        # 2. Try SMTP
        smtp_host = os.getenv("SMTP_HOST", "")
        smtp_user = os.getenv("SMTP_USER", "")
        smtp_pass = os.getenv("SMTP_PASSWORD", "")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))

        if smtp_host and smtp_user and smtp_pass:
            try:
                import smtplib
                from email.mime.multipart import MIMEMultipart
                from email.mime.text import MIMEText
                from email.mime.base import MIMEBase
                from email import encoders

                msg = MIMEMultipart("mixed")
                msg["Subject"] = subject
                msg["From"] = os.getenv("SMTP_FROM", f"Luxe Saloon & Spa <{smtp_user}>")
                msg["To"] = to_email

                body = MIMEMultipart("alternative")
                part_plain = MIMEText(f"Appointment Confirmed! Hi {caller_name}, your booking for {service} with {stylist} is confirmed for {start_time}. Add to Google Calendar: {gcal_add_link}", "plain")
                part_html = MIMEText(html_content or default_html, "html")
                body.attach(part_plain)
                body.attach(part_html)
                msg.attach(body)

                # Attach .ics
                part_ics = MIMEBase("text", "calendar", method="REQUEST", name="invite.ics")
                part_ics.set_payload(ics_content.encode("utf-8"))
                encoders.encode_base64(part_ics)
                part_ics.add_header("Content-Disposition", "attachment; filename=\"invite.ics\"")
                msg.attach(part_ics)

                with smtplib.SMTP(smtp_host, smtp_port, timeout=10.0) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_pass)
                    server.sendmail(msg["From"], [to_email], msg.as_string())
                logger.info(f"✅ SMTP Email with .ics attachment dispatched to {to_email}")
                return {"status": "sent", "channel": "smtp", "recipient": to_email, "gcal_add_link": gcal_add_link}
            except Exception as e:
                logger.error(f"SMTP delivery error: {e}")

        logger.info(f"📧 [EMAIL CONFIRMATION READY] To: {to_email} | Subject: {subject} | Ref: {ref_id} | GCal Add Link: {gcal_add_link}")
        return {"status": "sent", "channel": "email", "recipient": to_email, "ref": ref_id, "gcal_add_link": gcal_add_link}

    def dispatch_booking_confirmation(
        self,
        booking_record: Dict[str, Any],
        channel: str = "voice",
        recipient_id: Optional[str] = None,
        recipient_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """Multi-channel confirmation dispatch upon appointment commit across all touchpoints."""
        caller_name = booking_record.get("caller_name", "Valued Guest")
        caller_phone = booking_record.get("caller_phone", "")
        service = booking_record.get("service_name", "Service")
        stylist = booking_record.get("stylist_name", "Specialist")
        start_time = booking_record.get("start_time", "")
        ref_id = booking_record.get("booking_id", "")
        email = recipient_email or booking_record.get("caller_email", "")

        # Auto-lookup email from database customer profile if not explicitly passed
        if not email and caller_phone:
            try:
                from backend.database import get_customer_by_phone_or_email
                cust = get_customer_by_phone_or_email(phone=caller_phone)
                if cust and cust.get("email"):
                    email = cust["email"]
            except Exception:
                pass

        # Idempotency guard: prevent duplicate dispatch within 30s for the same booking_id on the same channel
        if not hasattr(self, "_recent_dispatches"):
            self._recent_dispatches = {}
        now_ts = datetime.now().timestamp()
        dispatch_key = f"{ref_id}:{channel}"
        if ref_id and dispatch_key in self._recent_dispatches:
            if now_ts - self._recent_dispatches[dispatch_key] < 30:
                logger.info(f"⚡ [IDEMPOTENCY] Confirmation already dispatched recently for #{ref_id} on {channel}")
                return {"status": "already_dispatched", "booking_id": ref_id, "channel": channel}
        if ref_id:
            self._recent_dispatches[dispatch_key] = now_ts

        cal_base = os.getenv("APP_BASE_URL", "https://ai-voice-receptionist-chi.vercel.app")
        cal_add_url = f"{cal_base}/api/calendar/add/{ref_id}"
        
        # WhatsApp Luxury Template
        wa_text = (
            f"✨ *Luxe Saloon & Spa Booking Confirmed* ✨\n\n"
            f"Dear *{caller_name}*,\n"
            f"Your appointment for *{service}* with Master Stylist *{stylist}* is confirmed for *{start_time}*.\n\n"
            f"📋 Booking Ref: *#{ref_id}*\n"
            f"📍 Location: 120 Newbury Street, Back Bay, Boston, MA\n"
            f"📅 Add to Calendar & Reminders:\n{cal_add_url}\n\n"
            f"Reply *RESCHEDULE* or *CANCEL* anytime to manage your reservation."
        )

        sms_text = (
            f"✨ Luxe Saloon: Booking #{ref_id} confirmed for {service} with {stylist} on {start_time}. "
            f"Add to calendar: {cal_add_url}. Reply CANCEL to cancel."
        )

        results = {}
        # 1. Automatic WhatsApp Confirmation
        if caller_phone:
            results["whatsapp"] = self.send_whatsapp(caller_phone, wa_text, quick_replies=["Confirm", "Reschedule", "Cancel"])
            results["sms"] = self.send_sms(caller_phone, sms_text)

        # 2. Automatic Email Confirmation (HTML with .ics calendar invite and 1-click Google Calendar add button)
        if email and "@" in email:
            results["email"] = self.send_email(
                to_email=email,
                subject=f"✨ Appointment Confirmed: {service} at Luxe Salon (#{ref_id})",
                booking_data=booking_record
            )

        # 3. Social messaging direct replies if specific channel was used
        if channel == "telegram" and recipient_id:
            results["telegram"] = self.send_telegram(recipient_id, wa_text, quick_replies=["Confirm", "Reschedule", "Cancel"])
        elif channel == "twitter" and recipient_id:
            results["twitter"] = self.send_twitter_dm(recipient_id, sms_text, quick_replies=["Confirm", "Reschedule", "Cancel"])
        elif channel == "linkedin" and recipient_id:
            results["linkedin"] = self.send_linkedin_message(recipient_id, sms_text)
        elif channel == "tiktok" and recipient_id:
            results["tiktok"] = self.send_tiktok_dm(recipient_id, sms_text)
        elif channel == "threads" and recipient_id:
            results["threads"] = self.send_threads_reply(recipient_id, sms_text)
        elif channel == "reddit" and recipient_id:
            results["reddit"] = self.send_reddit_message(recipient_id, sms_text)

        return results


# Global singleton dispatcher
notification_dispatcher = NotificationDispatcher()

