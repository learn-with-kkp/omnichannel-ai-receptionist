#!/usr/bin/env python3
"""
Interactive Setup Wizard: Connect Your Own Social & Meta Accounts
Validates tokens live against external APIs, saves to .env, syncs to Vercel, and redeploys.
"""

import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path
from dotenv import dotenv_values

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


def print_header(title: str):
    print("\n" + "=" * 70)
    print(f"  🚀 {title.upper()}")
    print("=" * 70)


def prompt_input(prompt: str, current_val: str = "") -> str:
    if current_val and not current_val.startswith("your_") and not current_val.startswith("sandbox_"):
        preview = current_val[:8] + "..." + current_val[-4:] if len(current_val) > 16 else current_val
        val = input(f"{prompt} [current: {preview}]: ").strip()
    else:
        val = input(f"{prompt}: ").strip()
    return val if val else current_val


def validate_telegram_token(token: str) -> bool:
    if not token or ":" not in token:
        return False
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            if data.get("ok"):
                bot_user = data.get("result", {}).get("username", "Unknown")
                print(f"   ✅ Valid Telegram Bot! Connected to @{bot_user}")
                return True
    except Exception as e:
        print(f"   ⚠️ Telegram validation note: {e}")
    return False


def validate_meta_token(token: str) -> bool:
    if not token or not token.startswith("EAA"):
        return False
    try:
        url = f"https://graph.facebook.com/v19.0/me?access_token={token}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            if "id" in data:
                print(f"   ✅ Valid Meta Access Token! Account Name: {data.get('name', 'Verified')}")
                return True
    except Exception as e:
        print(f"   ⚠️ Meta token note: {e}")
    return False


def update_env_file(updates: dict):
    lines = []
    if ENV_PATH.exists():
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()

    updated_keys = set()
    new_lines = []
    for line in lines:
        matched = False
        for k, v in updates.items():
            if line.startswith(f"{k}="):
                new_lines.append(f"{k}={v}\n")
                updated_keys.add(k)
                matched = True
                break
        if not matched:
            new_lines.append(line)

    # Append any keys that didn't exist in file
    for k, v in updates.items():
        if k not in updated_keys:
            new_lines.append(f"{k}={v}\n")

    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print(f"\n💾 Saved updated keys to {ENV_PATH}")


def main():
    print_header("Universal Omnichannel Account Connector")
    print("This wizard helps you link your personal/business accounts for:")
    print("1. Telegram (Fastest - 30 seconds)")
    print("2. Meta (Facebook Page, WhatsApp Cloud API, Instagram)")
    print("3. Twitter / X (Developer Portal)")
    print("4. LinkedIn & TikTok")
    print("\nPress Enter to skip any credential you haven't created yet.\n")

    current_env = dotenv_values(ENV_PATH) if ENV_PATH.exists() else {}
    updates = {}

    # 1. Telegram
    print_header("1. Telegram Bot (@BotFather)")
    print("Quick Steps:")
    print("  a. Open Telegram and search for @BotFather")
    print("  b. Send: /newbot")
    print("  c. Choose a Name and a Username (e.g. MyReceptionistBot)")
    print("  d. Copy the HTTP API Token it provides")
    tg_token = prompt_input("Enter your TELEGRAM_BOT_TOKEN", current_env.get("TELEGRAM_BOT_TOKEN", ""))
    if tg_token:
        validate_telegram_token(tg_token)
        updates["TELEGRAM_BOT_TOKEN"] = tg_token

    # 2. Meta: Facebook Page + WhatsApp + Instagram
    print_header("2. Meta: WhatsApp, Instagram & Facebook Page")
    print("Quick Steps:")
    print("  a. Go to: https://developers.facebook.com/apps")
    print("  b. Click 'Create App' -> 'Other' -> 'Business'")
    print("  c. Under Add Products, add 'WhatsApp'")
    print("  d. In WhatsApp -> API Setup, copy the 'Phone number ID'")
    print("  e. In your Facebook Page -> About, copy 'Page ID'")
    
    wa_phone_id = prompt_input("Enter WHATSAPP_PHONE_NUMBER_ID", current_env.get("WHATSAPP_PHONE_NUMBER_ID", ""))
    if wa_phone_id:
        updates["WHATSAPP_PHONE_NUMBER_ID"] = wa_phone_id

    page_id = prompt_input("Enter META_PAGE_ID (Facebook Page ID)", current_env.get("META_PAGE_ID", ""))
    if page_id:
        updates["META_PAGE_ID"] = page_id

    ig_id = prompt_input("Enter INSTAGRAM_ACCOUNT_ID (Professional Account ID)", current_env.get("INSTAGRAM_ACCOUNT_ID", ""))
    if ig_id:
        updates["INSTAGRAM_ACCOUNT_ID"] = ig_id

    meta_token = prompt_input("Enter META_ACCESS_TOKEN (System User Token)", current_env.get("META_ACCESS_TOKEN", ""))
    if meta_token:
        validate_meta_token(meta_token)
        updates["META_ACCESS_TOKEN"] = meta_token

    # 3. Twitter / X
    print_header("3. Twitter / X Developer Account")
    print("Quick Steps: https://developer.x.com -> Developer Portal -> Create App")
    tw_key = prompt_input("Enter TWITTER_API_KEY", current_env.get("TWITTER_API_KEY", ""))
    tw_secret = prompt_input("Enter TWITTER_API_SECRET", current_env.get("TWITTER_API_SECRET", ""))
    tw_bearer = prompt_input("Enter TWITTER_BEARER_TOKEN", current_env.get("TWITTER_BEARER_TOKEN", ""))
    if tw_key: updates["TWITTER_API_KEY"] = tw_key
    if tw_secret: updates["TWITTER_API_SECRET"] = tw_secret
    if tw_bearer: updates["TWITTER_BEARER_TOKEN"] = tw_bearer

    # 4. Save and Sync
    if updates:
        update_env_file(updates)

        sync_now = input("\nDo you want to sync these changes to Vercel production now? [Y/n]: ").strip().lower()
        if sync_now in ("", "y", "yes"):
            print("🚀 Syncing to Vercel Production...")
            import subprocess
            subprocess.run([sys.executable, str(Path(__file__).parent / "sync_env_to_vercel.py")])
            print("📦 Triggering Vercel deployment...")
            subprocess.run(["vercel", "--prod", "--yes"])
            print("\n🎉 Deployment complete! Visit https://ai-voice-receptionist.kishor.tech")
    else:
        print("\nNo changes made.")

if __name__ == "__main__":
    main()
