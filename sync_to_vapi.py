#!/usr/bin/env python3
"""
Sync Assistant Config directly to Vapi REST API.
Synchronizes Sophia (Front Desk) and Marcus (Salon Director & VIP Stylist),
injects dynamic calendar dates, attaches all core tools, sets stopSpeakingPlan for barge-in,
and updates Squad definitions.

Usage:
    python3 sync_to_vapi.py              # Syncs both Sophia and Marcus
    python3 sync_to_vapi.py --sophia     # Syncs only Sophia
    python3 sync_to_vapi.py --marcus     # Syncs only Marcus
    python3 sync_to_vapi.py --all        # Syncs both Sophia, Marcus and Squad
"""

import os
import sys
import json
import argparse
from datetime import datetime
import httpx
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
VAPI_DIR = BASE_DIR / "vapi"

VAPI_API_KEY = os.getenv("VAPI_PRIVATE_API_KEY") or os.getenv("VAPI_API_KEY")
SOPHIA_ID = os.getenv("VAPI_SOPHIA_ASSISTANT_ID") or os.getenv("VAPI_ASSISTANT_ID", "b9242970-fbef-4991-8e94-4e59ebd4ab47")
MARCUS_ID = os.getenv("VAPI_MARCUS_ASSISTANT_ID", "f8b6b7fc-ce8e-452c-bb8b-90b27bedb8cb")
SQUAD_ID = os.getenv("VAPI_SQUAD_ID", "816b5fbf-8eb1-4e26-805b-3cc6caade9ce")

TRANSFER_TO_MARCUS_TOOL = os.getenv("VAPI_TOOL_TRANSFER_MARCUS", "01bd1df8-f0c2-4640-bc65-4371a2e4e353")
TRANSFER_TO_SOPHIA_TOOL = os.getenv("VAPI_TOOL_TRANSFER_SOPHIA", "c402a27a-cae3-48ce-817c-c4f0070def32")

VALID_TOOLS = [
    os.getenv("VAPI_TOOL_CHECK_AVAILABILITY", "6c0d28b5-1258-45b7-97a5-a7fe981deff5"),  # check_availability
    os.getenv("VAPI_TOOL_BOOK_APPOINTMENT", "5477f565-44fd-4041-a39d-4a63ab165f40"),    # book_appointment
    os.getenv("VAPI_TOOL_LOOKUP_APPOINTMENT", "9df322c5-64af-44a7-b82f-105fb11e17ac"),  # lookup_appointment
    os.getenv("VAPI_TOOL_RESCHEDULE_APPOINTMENT", "c330c825-a0f6-40cb-9225-eb72ca655025"),  # reschedule_appointment
    os.getenv("VAPI_TOOL_CANCEL_APPOINTMENT", "fca2e93e-b963-469c-beaf-c4d4f9ee1f61"),  # cancel_appointment
    os.getenv("VAPI_TOOL_SEND_TEXT", "d4a55cbb-2c60-44e2-b916-15931d07f091"),            # send_text
    os.getenv("VAPI_TOOL_KNOWLEDGE", "cf4d3198-b52a-44b8-ab16-1ccde345e2f9"),            # query_knowledge_base
    os.getenv("VAPI_TOOL_END_CALL", "d72cf825-1222-42cf-b3f7-843c3a06deb4"),             # end_call
]

STOP_SPEAKING_PLAN = {
    "numWords": 1,
    "voiceSeconds": 0.2,
    "backoffSeconds": 0.5
}


def load_prompt_with_date(prompt_path: Path) -> str:
    """Reads markdown prompt and injects today's live calendar date."""
    content = prompt_path.read_text(encoding="utf-8")
    now = datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    
    # Prepend or replace dynamic date anchor
    anchor = f"# Temporal Anchor & Live Calendar Date\n- TODAY IS {date_str.upper()}. Current Year is {now.year}.\n- Current Time is morning in Boston, MA (Eastern Time).\n- All booking requests for today or upcoming dates belong to {now.year}.\n\n"
    return anchor + content


def sync_assistant(name: str, config_file: Path, prompt_file: Path, assistant_id: str, client: httpx.Client, headers: dict, extra_tools: list = None):
    if not config_file.exists():
        print(f"⚠️ Config file not found for {name}: {config_file}")
        return

    with open(config_file, "r") as f:
        payload = json.load(f)

    prompt_content = load_prompt_with_date(prompt_file)

    tool_ids = list(VALID_TOOLS)
    if extra_tools:
        tool_ids.extend(extra_tools)

    # Clean payload for update
    update_payload = {
        "name": payload.get("name"),
        "firstMessage": payload.get("firstMessage"),
        "model": {
            "provider": "openai",
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "system",
                    "content": prompt_content
                }
            ],
            "toolIds": tool_ids
        },
        "voice": payload.get("voice"),
        "transcriber": payload.get("transcriber"),
        "stopSpeakingPlan": STOP_SPEAKING_PLAN,
        "backgroundDenoisingEnabled": True,
        "serverUrl": "https://ai-voice-receptionist.kishor.tech/webhook/vapi-tools",
        "server": {
            "url": "https://ai-voice-receptionist.kishor.tech/webhook/vapi-tools",
            "timeoutSeconds": 20
        }
    }

    # Also update the local config file
    payload["model"] = update_payload["model"]
    payload["stopSpeakingPlan"] = STOP_SPEAKING_PLAN
    payload["serverUrl"] = update_payload["serverUrl"]
    payload["server"] = update_payload["server"]
    with open(config_file, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"\n🔄 Syncing {name} (Assistant ID: {assistant_id})...")
    url = f"https://api.vapi.ai/assistant/{assistant_id}"
    resp = client.patch(url, headers=headers, json=update_payload)

    if resp.status_code in (200, 201):
        data = resp.json()
        print(f"✅ {name} synced successfully!")
        print(f"   ID: {data.get('id')}")
        print(f"   Name: {data.get('name')}")
        print(f"   Model Messages: {len(data.get('model', {}).get('messages', []))} system prompt loaded ({len(prompt_content)} chars)")
        print(f"   Tools: {len(data.get('model', {}).get('toolIds', []))} tools attached")
        print(f"   Voice: {data.get('voice', {}).get('provider')} / {data.get('voice', {}).get('voiceId')}")
        print(f"   StopSpeakingPlan: {data.get('stopSpeakingPlan')}")
    else:
        print(f"❌ Failed to sync {name}: HTTP {resp.status_code}")
        print(resp.text)


def sync_squad(squad_id: str, client: httpx.Client, headers: dict):
    print(f"\n🔄 Verifying Squad (Squad ID: {squad_id})...")
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
    url = f"https://api.vapi.ai/squad/{squad_id}"
    resp = client.patch(url, headers=headers, json=squad_payload)
    if resp.status_code in (200, 201):
        data = resp.json()
        print(f"✅ Squad '{data.get('name')}' synced successfully!")
        print(f"   Members: {len(data.get('members', []))}")
    else:
        print(f"❌ Failed to sync squad: HTTP {resp.status_code}")
        print(resp.text)


def main():
    parser = argparse.ArgumentParser(description="Sync Assistant Configs to Vapi REST API")
    parser.add_argument("--sophia", action="store_true", help="Sync only Sophia assistant")
    parser.add_argument("--marcus", action="store_true", help="Sync only Marcus assistant")
    parser.add_argument("--all", action="store_true", help="Sync both Sophia, Marcus and Squad (default)")
    args = parser.parse_args()

    if not VAPI_API_KEY:
        print("⚠️ VAPI_PRIVATE_API_KEY environment variable is not set.")
        print("   Please check your .env file.")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }

    client = httpx.Client(timeout=30.0)

    sync_all = args.all or (not args.sophia and not args.marcus)

    if sync_all or args.sophia:
        sophia_config = VAPI_DIR / "assistant_config.json"
        sophia_prompt = VAPI_DIR / "system_prompt.md"
        sync_assistant("Sophia (Front Desk Receptionist)", sophia_config, sophia_prompt, SOPHIA_ID, client, headers, extra_tools=[TRANSFER_TO_MARCUS_TOOL])

    if sync_all or args.marcus:
        marcus_config = VAPI_DIR / "marcus_assistant_config.json"
        marcus_prompt = VAPI_DIR / "marcus_prompt.md"
        sync_assistant("Marcus (Salon Director & VIP Stylist)", marcus_config, marcus_prompt, MARCUS_ID, client, headers, extra_tools=[TRANSFER_TO_SOPHIA_TOOL])

    if sync_all:
        sync_squad(SQUAD_ID, client, headers)


if __name__ == "__main__":
    main()
