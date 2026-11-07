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
        self.twilio_from_phone = self.vapi_phone_number or os.getenv("TWILIO_PHONE_NUMBER", "+18005550199")
        self.twilio_whatsapp_from = os.getenv("TWILIO_WHATSAPP_NUMBER", "+14155238886")

        # Meta Cloud APIs (WhatsApp, Messenger, Instagram)
        self.meta_access_token = os.getenv("META_ACCESS_TOKEN", os.getenv("WHATSAPP_TOKEN", ""))
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

        # Slack Webhook URL
        self.slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL", "")

    def is_twilio_configured(self) -> bool:
        return bool(self.twilio_account_sid and self.twilio_auth_token and not self.twilio_account_sid.startswith("your_"))

    def is_meta_configured(self) -> bool:
        return bool(self.meta_access_token and not self.meta_access_token.startswith("your_"))

    def send_slack_alert(self, channel: str = "#appointments", message: str = "", title: Optional[str] = None) -> Dict[str, Any]:
        """Dispatches an instant alert to a Slack channel via Webhook or structured logger."""
        if self.slack_webhook_url and not self.slack_webhook_url.startswith("your_"):
            try:
                import httpx
                payload = {
                    "channel": channel,
                    "text": f"*{title or 'Omnichannel Voice Receptionist Alert'}*\n{message}"
                }
                resp = httpx.post(self.slack_webhook_url, json=payload, timeout=5.0)
                if resp.status_code == 200:
                    logger.info(f"✅ Slack notification dispatched to {channel}")
                    return {"status": "sent", "channel": channel, "title": title}
            except Exception as e:
                logger.error(f"Slack webhook delivery error: {e}")
        logger.info(f"💬 [SIMULATION SLACK] Channel: {channel} | Title: {title} | Content: {message}")
        return {"status": "simulated", "channel": channel, "title": title, "content": message}

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

    def trigger_vapi_outbound_call(
        self,
        to_phone: str,
        customer_name: str = "Valued Guest",
        tenant_name: str = "Luxe Salon & Spa",
        first_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Initiates an automated outbound phone call via Vapi REST API."""
        vapi_key = os.getenv("VAPI_API_KEY")
        asst_id = os.getenv("VAPI_ASSISTANT_ID")
        phone_id = os.getenv("VAPI_PHONE_NUMBER_ID")

        if vapi_key and asst_id and phone_id and not vapi_key.startswith("your_"):
            try:
                import httpx
                payload = {
                    "assistantId": asst_id,
                    "phoneNumberId": phone_id,
                    "customer": {
                        "number": to_phone,
                        "name": customer_name
                    }
                }
                if first_message:
                    payload["assistantOverrides"] = {
                        "firstMessage": first_message
                    }
                with httpx.Client(timeout=15.0) as client:
                    resp = client.post(
                        "https://api.vapi.ai/call/phone",
                        headers={"Authorization": f"Bearer {vapi_key}", "Content-Type": "application/json"},
                        json=payload
                    )
                    if resp.status_code in (200, 201):
                        data = resp.json()
                        logger.info(f"🚀 [VAPI CALL] Outbound call placed to {to_phone} (ID: {data.get('id')})")
                        return {"status": "success", "call_id": data.get("id"), "to": to_phone, "provider": "vapi"}
                    else:
                        logger.warning(f"Vapi API call error {resp.status_code}: {resp.text}")
            except Exception as e:
                logger.error(f"Vapi outbound call failed: {e}")

        logger.info(f"📞 [SIMULATED VAPI CALL] Calling {to_phone} for {customer_name} at {tenant_name}")
        return {"status": "simulated", "to": to_phone, "provider": "vapi_simulation"}

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

    def dispatch_booking_confirmation(
        self,
        booking_record: Dict[str, Any],
        channel: str = "voice",
        recipient_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Multi-channel confirmation dispatch upon appointment commit across all touchpoints."""
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
        # 1. Phone based channels
        if caller_phone:
            results["sms"] = self.send_sms(caller_phone, msg)
            results["whatsapp"] = self.send_whatsapp(caller_phone, msg, quick_replies=["Confirm", "Reschedule", "Cancel"])

        # 2. Social messaging direct replies if specific channel was used
        if channel == "telegram" and recipient_id:
            results["telegram"] = self.send_telegram(recipient_id, msg, quick_replies=["Confirm", "Reschedule", "Cancel"])
        elif channel == "twitter" and recipient_id:
            results["twitter"] = self.send_twitter_dm(recipient_id, msg, quick_replies=["Confirm", "Reschedule", "Cancel"])
        elif channel == "linkedin" and recipient_id:
            results["linkedin"] = self.send_linkedin_message(recipient_id, msg)
        elif channel == "tiktok" and recipient_id:
            results["tiktok"] = self.send_tiktok_dm(recipient_id, msg)
        elif channel == "threads" and recipient_id:
            results["threads"] = self.send_threads_reply(recipient_id, msg)
        elif channel == "reddit" and recipient_id:
            results["reddit"] = self.send_reddit_message(recipient_id, msg)

        return results


# Global singleton dispatcher
notification_dispatcher = NotificationDispatcher()

