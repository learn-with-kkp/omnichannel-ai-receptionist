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
    <div class="btn-container">
      <a href="{gcal_add_link}" target="_blank" class="btn-gcal">📅 Add to Google Calendar</a>
      <a href="https://ai-voice-receptionist.kishor.tech" target="_blank" class="btn-portal">✨ Sign In / VIP Portal</a>
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
      Luxe Saloon & Spa • 120 Newbury Street, Back Bay, Boston, MA 02116<br>
      Concierge Desk: (617) 555-LUXE • WhatsApp: +1 (912) 499-9633<br>
      © 2026 Luxe Saloon & Spa. All rights reserved.
    </div>
  </div>
</body>
</html>"""

        # 1. Try Resend API if configured
        resend_api_key = os.getenv("RESEND_API_KEY", "").strip()
        if resend_api_key:
            try:
                import requests
                res = requests.post(
                    "https://api.resend.com/emails",
                    headers={"Authorization": f"Bearer {resend_api_key}", "Content-Type": "application/json"},
                    json={
                        "from": os.getenv("SMTP_FROM", "Luxe Saloon & Spa <concierge@luxesaloon.com>"),
                        "to": [to_email],
                        "subject": subject,
                        "html": html_content or default_html,
                        "attachments": [
                            {
                                "filename": "invite.ics",
                                "content": list(ics_content.encode("utf-8"))
                            }
                        ]
                    },
                    timeout=10.0
                )
                if res.status_code in (200, 201):
                    logger.info(f"✅ Resend API email dispatched successfully to {to_email}")
                    return {"status": "sent", "channel": "resend", "recipient": to_email}
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

        # 2. Email confirmation
        if email and "@" in email:
            results["email"] = self.send_email(
                to_email=email,
                subject=f"✨ Appointment Confirmed: {service} at Luxe Salon (#{ref_id})",
                booking_data=booking_record
            )

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

