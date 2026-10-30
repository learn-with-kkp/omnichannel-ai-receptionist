#!/usr/bin/env python3
"""
Salon Client Onboarding Automation Engine.
Quickly provisions a new salon client:
  1. Creates tenant record in SQLite/PostgreSQL
  2. Sets up services & stylist rosters
  3. Generates their customized Vapi Assistant JSON
"""

import sys
import os
import json
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.database import create_tenant, get_tenant

def onboard(name: str, phone: str, address: str, stylists: list, tenant_id: str = None):
    slug = tenant_id or name.lower().replace(" ", "_").replace("&", "and")[:16]
    
    services = [
        ("Womens Haircut", 45, 80),
        ("Mens Cut", 30, 45),
        ("Balayage", 150, 195),
        ("Full Highlights", 120, 160),
        ("Keratin Treatment", 120, 225)
    ]
    
    tenant = create_tenant(slug, name, phone, address, services, stylists)
    print(f"✅ Created tenant record: {tenant['name']} [{slug}]")

    # Generate tailored Vapi Assistant Configuration
    base_config_path = BASE_DIR / "vapi" / "assistant_config.json"
    with open(base_config_path, "r") as f:
        vapi_cfg = json.load(f)

    vapi_cfg["name"] = f"{name} Receptionist - Sophia"
    vapi_cfg["firstMessage"] = f"Thank you for calling {name}! My name is Sophia. How can I pamper you today?"
    
    # Custom system prompt
    stylist_str = ", ".join(stylists)
    custom_system_prompt = (
        f"# Identity & Persona\n"
        f"You are 'Sophia', the warm, professional, and attentive front-desk receptionist for '{name}' located at {address}.\n\n"
        f"# Tone & Voice Dynamics\n"
        f"- Keep answers concise: 1 to 2 spoken sentences maximum per turn.\n"
        f"- Sound welcoming, graceful, and natural.\n\n"
        f"# Stylists on Roster\n"
        f"- {stylist_str}\n\n"
        f"# Core Behavioral Guidelines\n"
        f"1. DISCOVERY FIRST: Ask for service and date/time preference.\n"
        f"2. ALWAYS call `check_availability` before confirming any opening.\n"
        f"3. Always ask for 10-digit caller phone number to lock in the booking."
    )
    vapi_cfg["model"]["messages"][0]["content"] = custom_system_prompt

    out_file = BASE_DIR / "vapi" / "tenants" / f"{slug}_assistant.json"
    with open(out_file, "w") as f:
        json.dump(vapi_cfg, f, indent=2)

    print(f"📄 Tailored Vapi Assistant Config written to:")
    print(f"   👉 {out_file}")
    print(f"🎉 {name} is ready for client demo or live deployment!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Onboard new salon client")
    parser.add_argument("--name", required=True, help="Salon Business Name (e.g. 'SoHo Cuts NYC')")
    parser.add_argument("--phone", required=True, help="Assigned Inbound Phone (e.g. '+12125550199')")
    parser.add_argument("--address", default="128 Prince Street, New York, NY", help="Physical address")
    parser.add_argument("--stylists", default="Elena,Marcus,Chloe", help="Comma-separated stylist names")
    parser.add_argument("--id", default=None, help="Custom tenant slug ID")

    args = parser.parse_args()
    stylists_list = [s.strip() for s in args.stylists.split(",") if s.strip()]
    onboard(args.name, args.phone, args.address, stylists_list, args.id)

