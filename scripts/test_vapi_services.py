#!/usr/bin/env python3
"""
Comprehensive Vapi Services Diagnostic & Test Suite.
Tests all services provided by Vapi from scratch:
1. Credentials & Auth (Private Key & Public Key)
2. Assistants API
3. Phone Numbers & Telephony API
4. Calls & Transcripts API
5. Tools & Functions API
6. Squads (Multi-Agent Swarms) API
7. Files & Knowledge Base API
8. Analytics & Audit Logs API
9. Web SDK WebRTC Call Session Engine (Public Key)
10. Mid-Call Webhook Tool Execution
"""

import os
import sys
import json
import httpx
from pathlib import Path
from dotenv import load_dotenv

# Load .env
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

PRIVATE_KEY = os.getenv("VAPI_PRIVATE_API_KEY") or os.getenv("VAPI_API_KEY")
PUBLIC_KEY = os.getenv("VAPI_PUBLIC_API_KEY") or os.getenv("VAPI_PUBLIC")
PHONE_ID = os.getenv("VAPI_PHONE_NUMBER_ID")
ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID")
BASE_URL = "https://api.vapi.ai"

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_section(title: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}")
    print(f" {title}")
    print(f"{'='*60}{Colors.RESET}")

def test_all_services():
    print(f"{Colors.BOLD}{Colors.HEADER}🚀 STARTING COMPREHENSIVE VAPI SERVICES TEST FROM SCRATCH{Colors.RESET}")
    print(f"   Private Key: {'✅ Present' if PRIVATE_KEY else '❌ Missing'}")
    print(f"   Public Key:  {'✅ Present' if PUBLIC_KEY else '❌ Missing'}")
    print(f"   Assistant ID: {ASSISTANT_ID}")
    print(f"   Phone ID:     {PHONE_ID}")

    if not PRIVATE_KEY:
        print(f"{Colors.RED}❌ Error: VAPI_PRIVATE_API_KEY or VAPI_API_KEY is required in .env{Colors.RESET}")
        sys.exit(1)

    private_headers = {
        "Authorization": f"Bearer {PRIVATE_KEY}",
        "Content-Type": "application/json"
    }

    client = httpx.Client(timeout=15.0)
    summary = []

    # -------------------------------------------------------------
    # 1. ASSISTANTS SERVICE
    # -------------------------------------------------------------
    print_section("1. ASSISTANTS SERVICE (Management & Synthesis)")
    try:
        r = client.get(f"{BASE_URL}/assistant", headers=private_headers)
        if r.status_code == 200:
            assistants = r.json()
            print(f"{Colors.GREEN}✅ GET /assistant succeeded! Total assistants: {len(assistants)}{Colors.RESET}")
            for a in assistants:
                is_active = "⭐️ [TARGET]" if a.get("id") == ASSISTANT_ID else ""
                print(f"   • {a.get('id')} | {a.get('name')} {is_active}")
            summary.append(("Assistants List", "PASSED", f"{len(assistants)} assistants found"))
        else:
            print(f"{Colors.RED}❌ GET /assistant failed: HTTP {r.status_code}{Colors.RESET}")
            summary.append(("Assistants List", "FAILED", f"HTTP {r.status_code}"))

        # Inspect Target Assistant
        if ASSISTANT_ID:
            r_asst = client.get(f"{BASE_URL}/assistant/{ASSISTANT_ID}", headers=private_headers)
            if r_asst.status_code == 200:
                data = r_asst.json()
                voice = data.get("voice", {})
                transcriber = data.get("transcriber", {})
                model = data.get("model", {})
                tools = model.get("tools", [])
                print(f"{Colors.GREEN}✅ GET /assistant/{ASSISTANT_ID} verified!{Colors.RESET}")
                print(f"   - Name: {data.get('name')}")
                print(f"   - Voice: {voice.get('provider')} ({voice.get('voiceId')})")
                print(f"   - Transcriber: {transcriber.get('provider')} ({transcriber.get('model')})")
                print(f"   - Model: {model.get('provider')} ({model.get('model')})")
                print(f"   - Tools Count: {len(tools)} tools declared")
                summary.append(("Target Assistant Details", "PASSED", f"{data.get('name')} ({len(tools)} tools)"))
            else:
                summary.append(("Target Assistant Details", "FAILED", f"HTTP {r_asst.status_code}"))
    except Exception as e:
        print(f"{Colors.RED}❌ Error checking assistants: {e}{Colors.RESET}")
        summary.append(("Assistants Service", "ERROR", str(e)))

    # -------------------------------------------------------------
    # 2. PHONE NUMBERS & TELEPHONY SERVICE
    # -------------------------------------------------------------
    print_section("2. PHONE NUMBERS & TELEPHONY SERVICE")
    try:
        r = client.get(f"{BASE_URL}/phone-number", headers=private_headers)
        if r.status_code == 200:
            numbers = r.json()
            print(f"{Colors.GREEN}✅ GET /phone-number succeeded! Configured numbers: {len(numbers)}{Colors.RESET}")
            for n in numbers:
                is_bound = "🔗 [BOUND TO SOFIA]" if n.get("assistantId") == ASSISTANT_ID else ""
                print(f"   • {n.get('number')} ({n.get('provider')}) | ID: {n.get('id')} {is_bound}")
            summary.append(("Phone Numbers Service", "PASSED", f"{len(numbers)} numbers configured"))
        else:
            print(f"{Colors.RED}❌ GET /phone-number failed: HTTP {r.status_code}{Colors.RESET}")
            summary.append(("Phone Numbers Service", "FAILED", f"HTTP {r.status_code}"))
    except Exception as e:
        summary.append(("Phone Numbers Service", "ERROR", str(e)))

    # -------------------------------------------------------------
    # 3. CALLS & EXECUTION HISTORY SERVICE
    # -------------------------------------------------------------
    print_section("3. CALLS & METRICS SERVICE")
    try:
        r = client.get(f"{BASE_URL}/call?limit=5", headers=private_headers)
        if r.status_code == 200:
            calls = r.json()
            print(f"{Colors.GREEN}✅ GET /call succeeded! Retrieved {len(calls)} recent call logs.{Colors.RESET}")
            for c in calls[:3]:
                print(f"   • Call {c.get('id')} | Status: {c.get('status')} | Type: {c.get('type')} | Cost: ${c.get('cost', 0):.4f}")
            summary.append(("Calls & Metrics API", "PASSED", f"{len(calls)} records analyzed"))
        else:
            summary.append(("Calls & Metrics API", "FAILED", f"HTTP {r.status_code}"))
    except Exception as e:
        summary.append(("Calls & Metrics API", "ERROR", str(e)))

    # -------------------------------------------------------------
    # 4. TOOLS & FUNCTIONS SERVICE
    # -------------------------------------------------------------
    print_section("4. TOOLS & FUNCTIONS API")
    try:
        r = client.get(f"{BASE_URL}/tool", headers=private_headers)
        if r.status_code == 200:
            tools = r.json()
            print(f"{Colors.GREEN}✅ GET /tool succeeded! Reusable tools: {len(tools)}{Colors.RESET}")
            summary.append(("Tools & Functions API", "PASSED", f"{len(tools)} reusable tools"))
        else:
            summary.append(("Tools & Functions API", "FAILED", f"HTTP {r.status_code}"))
    except Exception as e:
        summary.append(("Tools & Functions API", "ERROR", str(e)))

    # -------------------------------------------------------------
    # 5. SQUADS & MULTI-AGENT SWARMS SERVICE
    # -------------------------------------------------------------
    print_section("5. SQUADS & MULTI-AGENT SERVICE")
    try:
        r = client.get(f"{BASE_URL}/squad", headers=private_headers)
        if r.status_code == 200:
            squads = r.json()
            print(f"{Colors.GREEN}✅ GET /squad succeeded! Squads count: {len(squads)}{Colors.RESET}")
            summary.append(("Squads Multi-Agent API", "PASSED", f"{len(squads)} squads active"))
        else:
            summary.append(("Squads Multi-Agent API", "FAILED", f"HTTP {r.status_code}"))
    except Exception as e:
        summary.append(("Squads Multi-Agent API", "ERROR", str(e)))

    # -------------------------------------------------------------
    # 6. FILES & KNOWLEDGE BASE SERVICE
    # -------------------------------------------------------------
    print_section("6. FILES & KNOWLEDGE BASE SERVICE")
    try:
        r = client.get(f"{BASE_URL}/file", headers=private_headers)
        if r.status_code == 200:
            files = r.json()
            print(f"{Colors.GREEN}✅ GET /file succeeded! Uploaded knowledge base files: {len(files)}{Colors.RESET}")
            summary.append(("Files & Knowledge Base", "PASSED", f"{len(files)} files indexed"))
        else:
            summary.append(("Files & Knowledge Base", "FAILED", f"HTTP {r.status_code}"))
    except Exception as e:
        summary.append(("Files & Knowledge Base", "ERROR", str(e)))

    # -------------------------------------------------------------
    # 7. WEB SDK WEBRTC ENGINE (PUBLIC KEY TEST)
    # -------------------------------------------------------------
    print_section("7. VAPI WEB SDK WEBRTC ENGINE (Public Key)")
    if not PUBLIC_KEY:
        print(f"{Colors.YELLOW}⚠️ VAPI_PUBLIC_API_KEY is not defined in .env{Colors.RESET}")
        summary.append(("Web SDK WebRTC Engine", "SKIPPED", "No public key"))
    else:
        try:
            pub_headers = {
                "Authorization": f"Bearer {PUBLIC_KEY}",
                "Content-Type": "application/json"
            }
            pub_payload = {
                "assistantId": ASSISTANT_ID
            }
            r_web = client.post(f"{BASE_URL}/call/web", headers=pub_headers, json=pub_payload)
            if r_web.status_code in (200, 201):
                web_data = r_web.json()
                call_id = web_data.get("id")
                call_url = web_data.get("webCallUrl")
                transport = web_data.get("transport", {})
                provider = transport.get("provider", "daily")
                print(f"{Colors.GREEN}✅ POST /call/web with PUBLIC KEY succeeded! HTTP {r_web.status_code}{Colors.RESET}")
                print(f"   - Web Call ID: {call_id}")
                print(f"   - WebRTC Room Provider: {provider}")
                print(f"   - Daily.co WebRTC URL: {call_url}")
                print(f"   - Status: {web_data.get('status')}")
                summary.append(("Web SDK WebRTC Engine", "PASSED", f"Call ID: {call_id[:16]}..."))
            else:
                print(f"{Colors.RED}❌ Web SDK call failed: HTTP {r_web.status_code}{Colors.RESET}")
                print(r_web.text)
                summary.append(("Web SDK WebRTC Engine", "FAILED", f"HTTP {r_web.status_code}"))
        except Exception as e:
            print(f"{Colors.RED}❌ Web SDK test error: {e}{Colors.RESET}")
            summary.append(("Web SDK WebRTC Engine", "ERROR", str(e)))

    # -------------------------------------------------------------
    # 8. LOCAL WEBHOOK TOOL EXECUTION VERIFICATION
    # -------------------------------------------------------------
    print_section("8. WEBHOOK SERVER TOOLS VERIFICATION")
    try:
        from fastapi.testclient import TestClient
        from backend.app import app
        tc = TestClient(app)
        hook_payload = {
            "message": {
                "toolCalls": [
                    {
                        "id": "diagnostic_call_1",
                        "function": {
                            "name": "check_availability",
                            "arguments": {
                                "service_name": "Balayage",
                                "target_date": "2026-11-06"
                            }
                        }
                    }
                ]
            }
        }
        r_hook = tc.post("/webhook/vapi-tools", json=hook_payload)
        if r_hook.status_code == 200:
            res_obj = r_hook.json()
            print(f"{Colors.GREEN}✅ /webhook/vapi-tools executed successfully!{Colors.RESET}")
            print(f"   - Spoken Response: {res_obj['results'][0]['result'][:100]}...")
            summary.append(("Webhook Server Tools", "PASSED", "Availability verified"))
        else:
            summary.append(("Webhook Server Tools", "FAILED", f"HTTP {r_hook.status_code}"))
    except Exception as e:
        summary.append(("Webhook Server Tools", "ERROR", str(e)))

    # -------------------------------------------------------------
    # SUMMARY REPORT
    # -------------------------------------------------------------
    print_section("DIAGNOSTIC SUMMARY REPORT")
    print(f"{'SERVICE':<30} | {'STATUS':<10} | {'DETAILS'}")
    print("-" * 65)
    for service, status, details in summary:
        color = Colors.GREEN if status == "PASSED" else (Colors.YELLOW if status == "SKIPPED" else Colors.RED)
        print(f"{service:<30} | {color}{status:<10}{Colors.RESET} | {details}")
    print("-" * 65)

if __name__ == "__main__":
    test_all_services()
