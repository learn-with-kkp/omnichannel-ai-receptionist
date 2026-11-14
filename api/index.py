"""
Vercel Serverless Function Entry Point for Universal AI Voice Receptionist.
Mounts the FastAPI ASGI application with dynamic routing, Neon PostgreSQL connection,
and omnichannel webhooks.
"""

import os
import sys
from pathlib import Path

# Ensure project root is in Python module search path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if "/var/task" not in sys.path:
    sys.path.insert(0, "/var/task")

os.environ["VERCEL"] = "1"
if not os.environ.get("KKP_ENTERPRISE_LICENSE_KEY"):
    os.environ["KKP_ENTERPRISE_LICENSE_KEY"] = "KKP-ENTERPRISE-VOICE-AI-2026-X99F-AUTH-SECURE-KEY"

from backend.app import app

# Top-level ASGI app assignment for Vercel Python builder
app = app
