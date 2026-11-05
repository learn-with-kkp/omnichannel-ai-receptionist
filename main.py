"""
Root Application Entry Point for Vercel, Uvicorn, and Production Deployments.
"""

import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app import app

# Top-level ASGI app for Vercel and ASGI servers
app = app
