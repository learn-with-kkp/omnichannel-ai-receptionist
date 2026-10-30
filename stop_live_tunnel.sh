#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Stopping Salon Voice AI Backend and Cloudflare Tunnel..."

if [ -f ".cloudflared.pid" ]; then
    PID=$(cat .cloudflared.pid)
    kill "$PID" 2>/dev/null || true
    rm -f .cloudflared.pid
    echo "✅ Terminated cloudflared (PID: $PID)"
fi

if [ -f ".backend.pid" ]; then
    PID=$(cat .backend.pid)
    kill "$PID" 2>/dev/null || true
    rm -f .backend.pid
    echo "✅ Terminated FastAPI backend (PID: $PID)"
fi

# Clean port 8000 if still held
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    kill -9 $(lsof -Pi :8000 -sTCP:LISTEN -t) 2>/dev/null || true
    echo "✅ Port 8000 freed"
fi

rm -f .live_tunnel_url cloudflared.log backend.log
echo "✅ Everything stopped cleanly."

