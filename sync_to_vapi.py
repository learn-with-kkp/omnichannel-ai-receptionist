#!/usr/bin/env python3
"""
Sync Assistant Config directly to Vapi REST API.
Supports syncing Sophia (Front Desk) and Marcus (Salon Director & VIP Stylist).

Usage:
    python3 sync_to_vapi.py              # Syncs both Sophia and Marcus
    python3 sync_to_vapi.py --sophia     # Syncs only Sophia
    python3 sync_to_vapi.py --marcus     # Syncs only Marcus
    python3 sync_to_vapi.py --all        # Syncs both Sophia and Marcus
"""

import os
import sys
import json
import argparse
import httpx
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
VAPI_DIR = BASE_DIR / "vapi"

VAPI_API_KEY = os.getenv("VAPI_PRIVATE_API_KEY") or os.getenv("VAPI_API_KEY")
SOPHIA_ID = os.getenv("VAPI_SOPHIA_ASSISTANT_ID") or os.getenv("VAPI_ASSISTANT_ID", "47b92dd7-6751-4c12-b531-23adf3614d35")
MARCUS_ID = os.getenv("VAPI_MARCUS_ASSISTANT_ID", "b23fc3d1-5b92-44fb-97f0-4f66d2af2cc9")

def sync_assistant(name: str, config_file: Path, assistant_id: str, client: httpx.Client, headers: dict):
    if not config_file.exists():
        print(f"⚠️ Config file not found for {name}: {config_file}")
        return

    with open(config_file, "r") as f:
        payload = json.load(f)

    # Clean payload for update if needed
    update_payload = {
        "name": payload.get("name"),
        "firstMessage": payload.get("firstMessage"),
        "model": payload.get("model"),
        "voice": payload.get("voice"),
        "transcriber": payload.get("transcriber"),
        "backgroundDenoisingEnabled": payload.get("backgroundDenoisingEnabled", True),
        "serverUrl": payload.get("serverUrl", "https://ai-voice-receptionist.kishor.tech/webhook/vapi-tools"),
        "server": payload.get("server", {
            "url": "https://ai-voice-receptionist.kishor.tech/webhook/vapi-tools",
            "timeoutSeconds": 20
        })
    }

    print(f"\n🔄 Syncing {name} (Assistant ID: {assistant_id})...")
    url = f"https://api.vapi.ai/assistant/{assistant_id}"
    resp = client.patch(url, headers=headers, json=update_payload)

    if resp.status_code in (200, 201):
        data = resp.json()
        print(f"✅ {name} synced successfully!")
        print(f"   ID: {data.get('id')}")
        print(f"   Name: {data.get('name')}")
        print(f"   Version: {data.get('latestVersion')}")
        print(f"   Tools: {len(data.get('model', {}).get('toolIds', []))} tools attached")
        print(f"   Voice: {data.get('voice', {}).get('provider')} / {data.get('voice', {}).get('voiceId')}")
    else:
        print(f"❌ Failed to sync {name}: HTTP {resp.status_code}")
        print(resp.text)

def main():
    parser = argparse.ArgumentParser(description="Sync Assistant Configs to Vapi REST API")
    parser.add_argument("--sophia", action="store_true", help="Sync only Sophia assistant")
    parser.add_argument("--marcus", action="store_true", help="Sync only Marcus assistant")
    parser.add_argument("--all", action="store_true", help="Sync both Sophia and Marcus (default)")
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
        sync_assistant("Sophia (Front Desk Receptionist)", sophia_config, SOPHIA_ID, client, headers)

    if sync_all or args.marcus:
        marcus_config = VAPI_DIR / "marcus_assistant_config.json"
        sync_assistant("Marcus (Salon Director & VIP Stylist)", marcus_config, MARCUS_ID, client, headers)

if __name__ == "__main__":
    main()
