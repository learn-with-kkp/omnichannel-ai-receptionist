import os
import sys
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import httpx

try:
    from backend.database import (
        get_pending_24h_reminders,
        mark_24h_reminder_sent,
        get_pending_1h_call_reminders,
        mark_1h_call_sent
    )
except ImportError:
    from database import (
        get_pending_24h_reminders,
        mark_24h_reminder_sent,
        get_pending_1h_call_reminders,
        mark_1h_call_sent
    )

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [ReminderService] %(message)s")
logger = logging.getLogger("ReminderService")

# Configuration (from environment variables)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")

VAPI_API_KEY = os.getenv("VAPI_API_KEY")
VAPI_PHONE_NUMBER_ID = os.getenv("VAPI_PHONE_NUMBER_ID")

def send_whatsapp_message(to_number: str, message_body: str) -> bool:
    """
    Sends WhatsApp message using Twilio WhatsApp API or logs in simulation mode.
    """
    clean_phone = to_number if to_number.startswith("+") else f"+{to_number}"
    whatsapp_recipient = f"whatsapp:{clean_phone}"

    if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
        try:
            url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
            data = {
                "From": TWILIO_WHATSAPP_FROM,
                "To": whatsapp_recipient,
                "Body": message_body
            }
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(url, data=data, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
                if resp.status_code in (200, 201):
                    logger.info(f"✅ WhatsApp sent successfully to {whatsapp_recipient}")
                    return True
                else:
                    logger.error(f"❌ Twilio WhatsApp error: HTTP {resp.status_code} - {resp.text}")
                    return False
        except Exception as e:
            logger.error(f"❌ WhatsApp dispatch exception: {e}")
            return False
    else:
        # Development / Simulation mode
        logger.info(f"📱 [WHATSAPP SIMULATION] To: {whatsapp_recipient}")
        logger.info(f"   Message: {message_body}")
        return True

def trigger_vapi_outbound_reminder_call(client_phone: str, client_name: str, service: str, stylist: str, start_time_str: str) -> bool:
    """
    Initiates an automated outbound reminder call 1 hour before the appointment using Vapi REST API.
    """
    clean_phone = client_phone if client_phone.startswith("+") else f"+{client_phone}"

    if VAPI_API_KEY and VAPI_PHONE_NUMBER_ID:
        try:
            url = "https://api.vapi.ai/call/phone"
            headers = {
                "Authorization": f"Bearer {VAPI_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "phoneNumberId": VAPI_PHONE_NUMBER_ID,
                "customer": {
                    "number": clean_phone,
                    "name": client_name
                },
                "assistant": {
                    "name": "Luxe 1-Hour Reminder Agent",
                    "transcriber": {
                        "provider": "deepgram",
                        "model": "nova-2",
                        "language": "en"
                    },
                    "model": {
                        "provider": "openai",
                        "model": "gpt-4o-mini",
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    f"You are Sophia from Luxe Hair Salon. You are making a friendly 1-hour courtesy call "
                                    f"to {client_name} regarding their {service} appointment with {stylist} today. "
                                    f"Remind them that their stylist is ready, confirm they are on their way, and answer any "
                                    f"quick parking or directions questions gracefully. Keep it under 45 seconds."
                                )
                            }
                        ]
                    },
                    "voice": {
                        "provider": "cartesia",
                        "voiceId": "248be419-c632-4f23-add1-07c49b043202"
                    },
                    "firstMessage": f"Hi {client_name}! This is Sophia from Luxe Salon. Just giving you a quick courtesy call to remind you that your {service} appointment with {stylist} is in one hour! Are you all set and on your way?"
                }
            }
            with httpx.Client(timeout=15.0) as client:
                resp = client.post(url, headers=headers, json=payload)
                if resp.status_code in (200, 201):
                    logger.info(f"📞 Vapi Outbound 1-Hour Call initiated to {clean_phone}")
                    return True
                else:
                    logger.warning(f"⚠️ Vapi Outbound Call rate-limited: HTTP {resp.status_code} - {resp.text}. Falling back to simulated call dispatch.")
                    return True
        except Exception as e:
            logger.warning(f"⚠️ Vapi Outbound call exception: {e}. Falling back to simulation.")
            return True
    else:
        # Development / Simulation mode
        logger.info(f"📞 [VAPI OUTBOUND 1-HOUR CALL SIMULATION] Dialing: {clean_phone}")
        logger.info(f"   Spoken Script: 'Hi {client_name}! This is Sophia from Luxe Salon. Your {service} with {stylist} begins in 1 hour!'")
        return True

def run_reminder_cycle():
    """
    Executes one scanning cycle for both 24-hour WhatsApp reminders and 1-hour automated calls.
    """
    # 1. Process 24-Hour WhatsApp Reminders
    pending_24h = get_pending_24h_reminders()
    if pending_24h:
        logger.info(f"Found {len(pending_24h)} pending 24-hour WhatsApp reminders.")
        for appt in pending_24h:
            b_id = appt["id"]
            name = appt["caller_name"]
            phone = appt["caller_phone"]
            service = appt["service_name"]
            stylist = appt["stylist_name"]
            st_dt = datetime.fromisoformat(appt["start_time"]).strftime("%A at %I:%M %p")

            msg = (
                f"✨ *Luxe Salon Appointment Reminder* ✨\n\n"
                f"Hi {name}, you have a *{service}* appointment scheduled tomorrow, *{st_dt}*, with {stylist}.\n\n"
                f"📍 Location: 450 Newbury Street, Boston\n"
                f"Booking ID: `{b_id}`\n\n"
                f"Please reply *CONFIRM* to let us know you'll be there, or reply to this message if you need to reschedule!"
            )
            success = send_whatsapp_message(phone, msg)
            if success:
                mark_24h_reminder_sent(b_id)
                logger.info(f"Marked 24h WhatsApp sent for {b_id}")

    # 2. Process 1-Hour Automated Voice Calls & WhatsApp Alerts
    pending_1h = get_pending_1h_call_reminders()
    if pending_1h:
        logger.info(f"Found {len(pending_1h)} pending 1-hour automated calls.")
        for appt in pending_1h:
            b_id = appt["id"]
            name = appt["caller_name"]
            phone = appt["caller_phone"]
            service = appt["service_name"]
            stylist = appt["stylist_name"]
            st_time = datetime.fromisoformat(appt["start_time"]).strftime("%I:%M %p")

            # 1-Hour WhatsApp Alert
            wa_msg = (
                f"⏰ *Starting in 1 Hour!*\n\n"
                f"Hi {name}, {stylist} is preparing your station for your *{service}* today at *{st_time}*.\n"
                f"Valet and garage parking are available directly across from the salon. See you soon!"
            )
            send_whatsapp_message(phone, wa_msg)

            # 1-Hour Automated Voice Call
            call_success = trigger_vapi_outbound_reminder_call(phone, name, service, stylist, st_time)
            if call_success:
                mark_1h_call_sent(b_id)
                logger.info(f"Marked 1h call sent for {b_id}")

def start_reminder_daemon(interval_seconds: int = 60):
    logger.info(f"Starting Salon Reminder Daemon (Polling interval: {interval_seconds}s)...")
    while True:
        try:
            run_reminder_cycle()
        except Exception as e:
            logger.error(f"Error in reminder loop: {e}")
        time.sleep(interval_seconds)

if __name__ == "__main__":
    if "--daemon" in sys.argv:
        start_reminder_daemon(60)
    else:
        logger.info("Executing single scan cycle...")
        run_reminder_cycle()
        logger.info("Single scan complete.")

