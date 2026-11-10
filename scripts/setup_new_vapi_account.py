#!/usr/bin/env python3
"""
Full Automated Provisioning & Squad Connection for New Vapi Account.
Creates all tools, configures Sophia & Marcus, wires bidirectional Squad transfers,
attaches the phone number, and updates .env.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import httpx
from dotenv import load_dotenv, set_key

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)

API_KEY = os.getenv("VAPI_PRIVATE_API_KEY", "").strip()
SOPHIA_ID = os.getenv("VAPI_SOPHIA_ASSISTANT_ID", "").strip()
MARCUS_ID = os.getenv("VAPI_MARCUS_ASSISTANT_ID", "").strip()
SQUAD_ID = os.getenv("VAPI_SQUAD_ID", "").strip()
PHONE_NUMBER_ID = os.getenv("VAPI_PHONE_NUMBER_ID", "").strip()
SERVER_URL = "https://ai-voice-receptionist.kishor.tech/webhook/vapi-tools"

if not API_KEY:
    print("❌ VAPI_PRIVATE_API_KEY missing in .env")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def load_prompt_with_date(filename: str) -> str:
    path = BASE_DIR / "vapi" / filename
    content = path.read_text(encoding="utf-8")
    now = datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    anchor = f"# Temporal Anchor & Live Calendar Date\n- TODAY IS {date_str.upper()}. Current Year is {now.year}.\n- Current Time is morning in Boston, MA (Eastern Time).\n- All booking requests for today or upcoming dates belong to {now.year}.\n\n"
    return anchor + content

def run_setup():
    with httpx.Client(base_url="https://api.vapi.ai", headers=HEADERS, timeout=45.0) as client:
        print("🚀 Step 1: Querying existing tools in new account...")
        tools_res = client.get("/tool")
        existing_tools = { (t.get("function", {}).get("name") or t.get("type")): t.get("id") for t in tools_res.json() } if tools_res.status_code == 200 else {}
        print(f"Existing tools count: {len(existing_tools)}")

        # Tool 1: check_availability
        tool_ids = {}
        
        tools_to_create = [
            {
                "type": "function",
                "function": {
                    "name": "check_availability",
                    "description": "Checks real-time open appointment slots against Google Calendar and salon stylist schedules.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "service_name": { "type": "string", "description": "Salon service requested (e.g. Balayage, Womens Haircut, Keratin, HydraFacial)." },
                            "target_date": { "type": "string", "description": "Target date string (e.g. 'tomorrow', '2026-11-09', 'this Saturday')." },
                            "preferred_stylist": { "type": "string", "description": "Preferred stylist name (Marcus, Elena, Chloe, Sofia, or Any)." },
                            "preferred_time": { "type": "string", "description": "Optional preferred time of day (e.g. '2:00 PM', 'morning', 'afternoon')." }
                        },
                        "required": ["service_name"]
                    }
                },
                "server": { "url": SERVER_URL }
            },
            {
                "type": "function",
                "function": {
                    "name": "book_appointment",
                    "description": "Commits an appointment directly to Google Calendar, live Google Sheets, and sends instant email & WhatsApp confirmations.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "caller_name": { "type": "string", "description": "Full name of the caller." },
                            "caller_email": { "type": "string", "description": "Caller email address to receive immediate booking confirmation, receipt, and Google Calendar invite." },
                            "caller_phone": { "type": "string", "description": "Caller phone number in E.164 format (+1XXXXXXXXXX or international)." },
                            "service_name": { "type": "string", "description": "Selected salon service." },
                            "stylist_name": { "type": "string", "description": "Assigned stylist (Marcus, Elena, Chloe, Sofia, or Any)." },
                            "appointment_datetime": { "type": "string", "description": "ISO 8601 formatted datetime string (e.g. 2026-11-09T14:00:00)." }
                        },
                        "required": ["caller_name", "caller_phone", "service_name", "appointment_datetime"]
                    }
                },
                "server": { "url": SERVER_URL }
            },
            {
                "type": "function",
                "function": {
                    "name": "lookup_appointment",
                    "description": "Looks up existing appointment details for a client using their phone number or full name.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "phone_number": { "type": "string", "description": "Caller phone number in E.164 format." },
                            "customer_name": { "type": "string", "description": "Customer name to search for if phone number is unavailable." }
                        },
                        "required": []
                    }
                },
                "server": { "url": SERVER_URL }
            },
            {
                "type": "function",
                "function": {
                    "name": "reschedule_appointment",
                    "description": "Reschedules an existing confirmed appointment to a new date and time.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "phone_number": { "type": "string", "description": "Caller phone number." },
                            "new_datetime": { "type": "string", "description": "Target new ISO 8601 datetime string." },
                            "reason": { "type": "string", "description": "Reason for rescheduling (optional)." }
                        },
                        "required": ["phone_number", "new_datetime"]
                    }
                },
                "server": { "url": SERVER_URL }
            },
            {
                "type": "function",
                "function": {
                    "name": "cancel_appointment",
                    "description": "Cancels an existing appointment, releases the Google Calendar slot, and updates Google Sheets.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "phone_number": { "type": "string", "description": "Caller phone number." },
                            "cancellation_reason": { "type": "string", "description": "Brief reason for cancellation." }
                        },
                        "required": ["phone_number"]
                    }
                },
                "server": { "url": SERVER_URL }
            },
            {
                "type": "function",
                "function": {
                    "name": "send_text",
                    "description": "Sends an instant SMS or WhatsApp confirmation message with booking links or directions to the client's phone.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "recipient_phone": { "type": "string", "description": "Recipient phone number in E.164 format." },
                            "message_body": { "type": "string", "description": "Content of the text message." }
                        },
                        "required": ["recipient_phone", "message_body"]
                    }
                },
                "server": { "url": SERVER_URL }
            },
            {
                "type": "function",
                "function": {
                    "name": "query_knowledge_base",
                    "description": "Queries the salon knowledge base for treatments, pricing, parking, directions, and salon policies.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": { "type": "string", "description": "The customer's question regarding services, pricing, or policies." }
                        },
                        "required": ["query"]
                    }
                },
                "server": { "url": SERVER_URL }
            },
            {
                "type": "endCall",
                "function": {
                    "name": "end_call",
                    "parameters": { "type": "object", "properties": {}, "required": [] }
                },
                "messages": [{ "type": "request-start", "blocking": False }]
            }
        ]

        created_tool_ids = []
        for t_spec in tools_to_create:
            name_key = t_spec.get("function", {}).get("name") or t_spec.get("type")
            res = client.post("/tool", json=t_spec)
            if res.status_code in (200, 201):
                tid = res.json().get("id")
                tool_ids[name_key] = tid
                created_tool_ids.append(tid)
                print(f"  ✅ Created tool: {name_key} -> {tid}")
            else:
                print(f"  ❌ Failed creating {name_key}: {res.status_code} {res.text}")

        # Transfer tool: transferCall to Marcus (used by Sophia)
        transfer_to_marcus_spec = {
            "type": "transferCall",
            "destinations": [
                {
                    "type": "assistant",
                    "assistantName": "Luxe Salon Director - Marcus",
                    "description": "Transfer the call to Marcus Vance, Creative Hair Director & Master Colorist, whenever the caller asks to talk to Marcus, asks for Marcus, wants hair coloring, balayage, or haircut consultation with Marcus, asks for the director or manager, or has an escalation."
                }
            ]
        }
        res_tm = client.post("/tool", json=transfer_to_marcus_spec)
        transfer_to_marcus_id = res_tm.json().get("id") if res_tm.status_code in (200, 201) else None
        print(f"  ✅ Created transferCall to Marcus -> {transfer_to_marcus_id}")

        # Transfer tool: transferCall to Sophia (used by Marcus)
        transfer_to_sophia_spec = {
            "type": "transferCall",
            "destinations": [
                {
                    "type": "assistant",
                    "assistantName": "Luxe Salon Voice Receptionist - Sophia",
                    "description": "Transfer the call back to Sophia, Front Desk Voice Receptionist, whenever the caller asks to speak with Sophia, wants front desk scheduling, nails, facial, or general salon reception check-in."
                }
            ]
        }
        res_ts = client.post("/tool", json=transfer_to_sophia_spec)
        transfer_to_sophia_id = res_ts.json().get("id") if res_ts.status_code in (200, 201) else None
        print(f"  ✅ Created transferCall to Sophia -> {transfer_to_sophia_id}")

        # -------------------------------------------------------------
        # Step 2: Configure Sophia Assistant
        # -------------------------------------------------------------
        print("\n👩‍💼 Step 2: Configuring Sophia Assistant...")
        sophia_tools = list(created_tool_ids)
        if transfer_to_marcus_id:
            sophia_tools.append(transfer_to_marcus_id)

        sophia_prompt = load_prompt_with_date("system_prompt.md")
        sophia_payload = {
            "name": "Luxe Salon Voice Receptionist - Sophia",
            "firstMessage": "Thank you for calling Luxe Saloon & Spa on Newbury Street! My name is Sophia. How can I pamper you today?",
            "model": {
                "provider": "openai",
                "model": "gpt-4o",
                "messages": [{ "role": "system", "content": sophia_prompt }],
                "toolIds": sophia_tools
            },
            "voice": {
                "provider": "vapi",
                "voiceId": "Clara",
                "version": "2"
            },
            "transcriber": {
                "provider": "deepgram",
                "model": "nova-2",
                "language": "en-US",
                "keywords": ["Balayage:3", "Keratin:3", "Blowout:2", "Highlights:2", "Elena:2", "Marcus:2", "Chloe:2", "Luxe:2"]
            },
            "stopSpeakingPlan": { "numWords": 1, "voiceSeconds": 0.2, "backoffSeconds": 0.5 },
            "startSpeakingPlan": { "waitSeconds": 0.4 },
            "backgroundDenoisingEnabled": True,
            "backchannelingEnabled": True,
            "serverUrl": SERVER_URL,
            "server": { "url": SERVER_URL }
        }
        res_sophia = client.patch(f"/assistant/{SOPHIA_ID}", json=sophia_payload)
        if res_sophia.status_code == 200:
            print("  ✅ Sophia successfully updated with tools & prompts!")
        else:
            print(f"  ⚠️ Sophia update returned: {res_sophia.status_code} {res_sophia.text}")

        # -------------------------------------------------------------
        # Step 3: Configure Marcus Assistant
        # -------------------------------------------------------------
        print("\n🎨 Step 3: Configuring Marcus Assistant...")
        marcus_tools = list(created_tool_ids)
        if transfer_to_sophia_id:
            marcus_tools.append(transfer_to_sophia_id)

        marcus_prompt = load_prompt_with_date("marcus_prompt.md")
        marcus_payload = {
            "name": "Luxe Salon Director - Marcus",
            "firstMessage": "Hello, this is Marcus, Master Stylist and Salon Director at Luxe Newbury. Sophia mentioned you needed personal assistance—how can I take care of you today?",
            "model": {
                "provider": "openai",
                "model": "gpt-4o",
                "messages": [{ "role": "system", "content": marcus_prompt }],
                "toolIds": marcus_tools
            },
            "voice": {
                "provider": "vapi",
                "voiceId": "Elliot",
                "version": "2"
            },
            "transcriber": {
                "provider": "deepgram",
                "model": "nova-2",
                "language": "en-US",
                "keywords": ["Balayage:3", "Keratin:3", "Bridal:3", "Director:2", "Elena:2", "Marcus:2", "Luxe:2"]
            },
            "stopSpeakingPlan": { "numWords": 1, "voiceSeconds": 0.2, "backoffSeconds": 0.5 },
            "startSpeakingPlan": { "waitSeconds": 0.4 },
            "backgroundDenoisingEnabled": True,
            "backchannelingEnabled": True,
            "serverUrl": SERVER_URL,
            "server": { "url": SERVER_URL }
        }
        res_marcus = client.patch(f"/assistant/{MARCUS_ID}", json=marcus_payload)
        if res_marcus.status_code == 200:
            print("  ✅ Marcus successfully updated with tools & prompts!")
        else:
            print(f"  ⚠️ Marcus update returned: {res_marcus.status_code} {res_marcus.text}")

        # -------------------------------------------------------------
        # Step 4: Configure Squad with Bidirectional Handoff
        # -------------------------------------------------------------
        print("\n👥 Step 4: Configuring Squad with Bidirectional Routing...")
        squad_payload = {
            "name": "Luxe Salon Concierge & Escalations Squad",
            "members": [
                {
                    "assistantId": SOPHIA_ID,
                    "assistantDestinations": [
                        {
                            "type": "assistant",
                            "assistantName": "Luxe Salon Director - Marcus",
                            "description": "Transfer to Marcus Vance whenever the caller asks to talk to Marcus, asks for Marcus, wants hair coloring, balayage, or haircut consultation with Marcus, asks for the director or manager, has an escalation, or asks about bridal parties greater than 4 guests."
                        }
                    ]
                },
                {
                    "assistantId": MARCUS_ID,
                    "assistantDestinations": [
                        {
                            "type": "assistant",
                            "assistantName": "Luxe Salon Voice Receptionist - Sophia",
                            "description": "Transfer back to Sophia whenever the caller asks to speak with Sophia, wants front desk scheduling, nails, facial, or general salon reception check-in."
                        }
                    ]
                }
            ]
        }
        res_sq = client.patch(f"/squad/{SQUAD_ID}", json=squad_payload)
        if res_sq.status_code == 200:
            print("  ✅ Squad successfully updated with Sofia & Marcus linked!")
        else:
            print(f"  ⚠️ Squad update returned: {res_sq.status_code} {res_sq.text}")

        # -------------------------------------------------------------
        # Step 5: Attach Phone Number to Squad
        # -------------------------------------------------------------
        if PHONE_NUMBER_ID:
            print(f"\n📞 Step 5: Binding Phone Number ({PHONE_NUMBER_ID}) to Squad...")
            phone_payload = {
                "squadId": SQUAD_ID,
                "serverUrl": SERVER_URL
            }
            res_p = client.patch(f"/phone-number/{PHONE_NUMBER_ID}", json=phone_payload)
            if res_p.status_code == 200:
                print("  ✅ Inbound phone number bound to Squad!")
            else:
                # If squadId not directly accepted on phone number, bind to Sophia with transfer tools
                print(f"  ℹ️ Binding directly to Sophia ({SOPHIA_ID}) with Squad transfer enabled...")
                res_p2 = client.patch(f"/phone-number/{PHONE_NUMBER_ID}", json={"assistantId": SOPHIA_ID, "serverUrl": SERVER_URL})
                if res_p2.status_code == 200:
                    print("  ✅ Inbound phone number bound to Sophia!")
                else:
                    print(f"  ⚠️ Phone update result: {res_p2.status_code} {res_p2.text}")

        # -------------------------------------------------------------
        # Step 6: Save IDs to .env & sync_to_vapi.py
        # -------------------------------------------------------------
        print("\n💾 Step 6: Persisting Tool IDs and Assistant IDs...")
        set_key(str(ENV_PATH), "VAPI_ASSISTANT_ID", SOPHIA_ID)
        set_key(str(ENV_PATH), "VAPI_PUBLIC_KEY", os.getenv("VAPI_PUBLIC_API_KEY", ""))
        set_key(str(ENV_PATH), "VAPI_TOOL_CHECK_AVAILABILITY", tool_ids.get("check_availability", ""))
        set_key(str(ENV_PATH), "VAPI_TOOL_BOOK_APPOINTMENT", tool_ids.get("book_appointment", ""))
        set_key(str(ENV_PATH), "VAPI_TOOL_LOOKUP_APPOINTMENT", tool_ids.get("lookup_appointment", ""))
        set_key(str(ENV_PATH), "VAPI_TOOL_RESCHEDULE_APPOINTMENT", tool_ids.get("reschedule_appointment", ""))
        set_key(str(ENV_PATH), "VAPI_TOOL_CANCEL_APPOINTMENT", tool_ids.get("cancel_appointment", ""))
        set_key(str(ENV_PATH), "VAPI_TOOL_SEND_TEXT", tool_ids.get("send_text", ""))
        set_key(str(ENV_PATH), "VAPI_TOOL_KNOWLEDGE", tool_ids.get("query_knowledge_base", ""))
        set_key(str(ENV_PATH), "VAPI_TOOL_END_CALL", tool_ids.get("end_call", ""))
        if transfer_to_marcus_id:
            set_key(str(ENV_PATH), "VAPI_TOOL_TRANSFER_MARCUS", transfer_to_marcus_id)
        if transfer_to_sophia_id:
            set_key(str(ENV_PATH), "VAPI_TOOL_TRANSFER_SOPHIA", transfer_to_sophia_id)
        print("  ✅ .env file successfully updated!")

if __name__ == "__main__":
    run_setup()

