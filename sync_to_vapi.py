#!/usr/bin/env python3
"""
Sync Assistant Config directly to Vapi REST API.
Usage:
    export VAPI_API_KEY="your-vapi-private-api-key"
    python3 sync_to_vapi.py [--assistant-id <id>]
"""

import os
import sys
import json
import httpx
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "vapi" / "assistant_config.json"

VAPI_API_KEY = os.getenv("VAPI_API_KEY")
VAPI_ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID")

def sync():
    if not VAPI_API_KEY:
        print("⚠️ VAPI_API_KEY environment variable is not set.")
        print("   To push automatically to Vapi, run:")
        print("   export VAPI_API_KEY=\"your_key_here\"")
        print("   python3 sync_to_vapi.py")
        sys.exit(0)

    with open(CONFIG_FILE, "r") as f:
        payload = json.load(f)

    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }

    client = httpx.Client(timeout=30.0)

    if VAPI_ASSISTANT_ID:
        print(f"🔄 Updating existing Vapi Assistant: {VAPI_ASSISTANT_ID}...")
        url = f"https://api.vapi.ai/assistant/{VAPI_ASSISTANT_ID}"
        resp = client.patch(url, headers=headers, json=payload)
    else:
        print("🚀 Creating new Vapi Assistant...")
        url = "https://api.vapi.ai/assistant"
        resp = client.post(url, headers=headers, json=payload)

    if resp.status_code in (200, 201):
        data = resp.json()
        print(f"✅ Assistant synced successfully! Assistant ID: {data.get('id')}")
        print(f"   Name: {data.get('name')}")
        print(f"   Server URL: {data.get('serverUrl')}")
    else:
        print(f"❌ Failed to sync to Vapi: HTTP {resp.status_code}")
        print(resp.text)

if __name__ == "__main__":
    sync()

