#!/usr/bin/env python3
"""
Sync local .env configuration directly into Vercel Project Environment Variables.
Ensures production deployment on ai-voice-receptionist.kishor.tech has all live API keys.
"""

import os
import subprocess
import sys
from pathlib import Path
from dotenv import dotenv_values

def main():
    env_file = Path(__file__).resolve().parent.parent / ".env"
    if not env_file.exists():
        print(f"❌ Error: {env_file} does not exist.")
        sys.exit(1)

    print(f"📂 Loading variables from: {env_file}")
    values = dotenv_values(env_file)

    # Get current existing env vars in Vercel
    res = subprocess.run(["vercel", "env", "ls", "production"], capture_output=True, text=True)
    existing_vars = set()
    for line in res.stdout.splitlines():
        parts = line.split()
        if parts and parts[0] != "name" and parts[0] != ">" and parts[0] != "Vercel":
            existing_vars.add(parts[0])

    print(f"ℹ️ Currently configured in Vercel: {len(existing_vars)} keys.")

    synced_count = 0
    for key, val in values.items():
        if not key or val is None or val == "":
            continue
        # Remove if exists to update with fresh value
        if key in existing_vars:
            subprocess.run(["vercel", "env", "rm", key, "production", "-y"], capture_output=True, text=True)
        
        # Add variable to production
        p = subprocess.Popen(["vercel", "env", "add", key, "production"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = p.communicate(input=val)
        if p.returncode == 0:
            print(f"✅ Synced: {key}")
            synced_count += 1
        else:
            print(f"⚠️ Failed to sync {key}: {stderr.strip() or stdout.strip()}")

    print(f"\n🎉 Successfully synced {synced_count} environment variables to Vercel Production!")

if __name__ == "__main__":
    main()

