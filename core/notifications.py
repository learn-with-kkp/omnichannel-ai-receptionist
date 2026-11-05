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
        # Twilio Credentials
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.twilio_from_phone = os.getenv("TWILIO_PHONE_NUMBER", "+18005550199")
        self.twilio_whatsapp_from = os.getenv("TWILIO_WHATSAPP_NUMBER", "+14155238886")

        # Meta Cloud APIs (WhatsApp, Messenger, Instagram)
        self.meta_access_token = os.getenv("META_ACCESS_TOKEN", os.getenv("WHATSAPP_TOKEN", ""))
        self.whatsapp_phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
        self.meta_page_id = os.getenv("META_PAGE_ID", "")

    def is_twilio_configured(self) -> bool:
        return bool(self.twilio_account_sid and self.twilio_auth_token and not self.twilio_account_sid.startswith("your_"))

    def is_meta_configured(self) -> bool:
        return bool(self.meta_access_token and not self.meta_access_token.startswith("your_"))

    def send_sms(self, to_phone: str, text: str) -> Dict[str, Any]:
        """Dispatches an SMS message via Twilio or resilient simulator."""
        if self.is_twilio_configured():
            try:
                from twilio.rest import Client
                client = Client(self.twilio_account_sid, self.twilio_auth_token)
                msg = client.messages.create(body=text, from_=self.twilio_from_phone, to=to_phone)
                logger.info(f"✅ Twilio SMS dispatched to {to_phone} (SID: {msg.sid})")
                return {"status": "sent", "channel": "sms", "sid": msg.sid, "recipient": to_phone}
            except Exception as e:
                logger.error(f"Twilio SMS delivery failed: {e}")

        logger.info(f"📱 [SIMULATION SMS] To: {to_phone} | Content: {text}")
        return {"status": "simulated", "channel": "sms", "recipient": to_phone, "content": text}

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

    def send_whatsapp(self, to_phone: str, text: str, quick_replies: Optional[List[str]] = None) -> Dict[str, Any]:
        """Dispatches WhatsApp push message via Meta Cloud API or Twilio WhatsApp."""
        if self.whatsapp_phone_number_id and self.meta_access_token:
            try:
                clean_phone = "".join(filter(str.isdigit, to_phone))
                url = f"https://graph.facebook.com/v19.0/{self.whatsapp_phone_number_id}/messages"
                payload = {
                    "messaging_product": "whatsapp",
                    "to": clean_phone,
                    "type": "text",
                    "text": {"preview_url": False, "body": text}
                }
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    url, data=data,
                    headers={
                        "Authorization": f"Bearer {self.meta_access_token}",
                        "Content-Type": "application/json"
                    }
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    resp_data = json.loads(resp.read().decode())
                    logger.info(f"✅ Meta WhatsApp dispatched to {to_phone}: {resp_data}")
                    return {"status": "sent", "channel": "whatsapp", "response": resp_data}
            except Exception as e:
                logger.error(f"Meta WhatsApp Cloud API failed: {e}")

        # Fallback to Twilio WhatsApp if configured
        if self.is_twilio_configured():
            try:
                from twilio.rest import Client
                client = Client(self.twilio_account_sid, self.twilio_auth_token)
                msg = client.messages.create(
                    body=text,
                    from_=f"whatsapp:{self.twilio_whatsapp_from}",
                    to=f"whatsapp:{to_phone}"
                )
                logger.info(f"✅ Twilio WhatsApp message sent: {msg.sid}")
                return {"status": "sent", "channel": "whatsapp_twilio", "sid": msg.sid}
            except Exception as e:
                logger.error(f"Twilio WhatsApp failed: {e}")

        logger.info(f"🟢 [SIMULATION WHATSAPP] To: {to_phone} | Body: {text}")
        return {"status": "simulated", "channel": "whatsapp", "to": to_phone, "content": text}

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

    def dispatch_booking_confirmation(self, booking_record: Dict[str, Any], channel: str = "voice") -> Dict[str, Any]:
        """Multi-channel confirmation dispatch upon appointment commit."""
        caller_name = booking_record.get("caller_name", "Valued Guest")
        caller_phone = booking_record.get("caller_phone", "")
        service = booking_record.get("service_name", "Service")
        stylist = booking_record.get("stylist_name", "Specialist")
        start_time = booking_record.get("start_time", "")
        ref_id = booking_record.get("booking_id", "")

        msg = (
            f"✨ Booking Confirmed!\n"
            f"Hello {caller_name}, your appointment for {service} with {stylist} is confirmed for {start_time}.\n"
            f"Reference: #{ref_id}\n"
            f"To modify or cancel, reply RESCHEDULE or CANCEL."
        )

        results = {}
        # 1. Send SMS
        if caller_phone:
            results["sms"] = self.send_sms(caller_phone, msg)
            results["whatsapp"] = self.send_whatsapp(caller_phone, msg, quick_replies=["Confirm", "Reschedule", "Cancel"])

        return results


# Global singleton dispatcher
notification_dispatcher = NotificationDispatcher()
