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

from backend.app import app

# Top-level ASGI app assignment for Vercel Python builder
app = app
