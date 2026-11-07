#!/usr/bin/env python3
"""
Direct CLI utility to send an outbound SMS message from VAPI_PHONE_NUMBER.
Usage:
    python3 scripts/send_message_from_vapi.py --to "+16175550199" --message "Hello from Luxe Salon!"
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Ensure salon-voice-ai-receptionist is in Python path
base_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(base_dir))

load_dotenv(dotenv_path=base_dir / ".env")

from core.notifications import notification_dispatcher


def main():
    parser = argparse.ArgumentParser(description="Send an SMS from VAPI_PHONE_NUMBER.")
    parser.add_argument("--to", required=True, help="Recipient phone number in E.164 format (e.g. +16175550199)")
    parser.add_argument("--message", required=True, help="Text message content to send")
    
    args = parser.parse_args()
    
    from_num = os.getenv("VAPI_PHONE_NUMBER") or os.getenv("TWILIO_PHONE_NUMBER", "+19124999633")
    print(f"🚀 Dispatching SMS from VAPI_PHONE_NUMBER ({from_num}) to {args.to}...")
    
    result = notification_dispatcher.send_sms(to_phone=args.to, text=args.message)
    
    print("\n📦 Result:")
    print(result)
    if result.get("status") == "sent":
        print(f"\n✅ Message sent successfully! SID: {result.get('sid')}")
    elif result.get("status") == "simulated":
        print(f"\n📱 Message dispatched in simulated test mode (configure live Twilio keys in .env to send live SMS).")
    else:
        print(f"\n⚠️ Delivery status: {result.get('status')}")


if __name__ == "__main__":
    main()
