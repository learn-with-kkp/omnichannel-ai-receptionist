#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export PATH="/opt/homebrew/bin:$PATH"

echo "=========================================================="
echo "💈 Starting Luxe Salon Voice AI Stack + Cloudflare Tunnel"
echo "=========================================================="

# 1. Check or start FastAPI backend
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚡ Port 8000 is already in use. Reusing active backend..."
else
    echo "🚀 Starting FastAPI backend on http://127.0.0.1:8000..."
    nohup "$SCRIPT_DIR/.venv/bin/uvicorn" backend.app:app --host 127.0.0.1 --port 8000 > backend.log 2>&1 &
    echo $! > .backend.pid
    sleep 1
fi

# 2. Wait for local health check
echo "🔍 Verifying local health..."
for i in {1..10}; do
    if curl -sf http://127.0.0.1:8000/health > /dev/null; then
        echo "✅ FastAPI Backend is HEALTHY at http://127.0.0.1:8000/health"
        break
    fi
    sleep 1
done

# 3. Terminate any previous cloudflared quick tunnel if running
if [ -f ".cloudflared.pid" ]; then
    OLD_PID=$(cat .cloudflared.pid)
    kill "$OLD_PID" 2>/dev/null || true
    rm -f .cloudflared.pid
fi

# 4. Start Cloudflare Tunnel
echo "🌐 Spawning Cloudflare Tunnel..."
rm -f cloudflared.log
nohup cloudflared tunnel --url http://127.0.0.1:8000 > cloudflared.log 2>&1 &
echo $! > .cloudflared.pid

# 5. Extract Public URL
echo "⏳ Waiting for Cloudflare tunnel assignment..."
TUNNEL_URL=""
for i in {1..20}; do
    if [ -f cloudflared.log ]; then
        FOUND=$(grep -o 'https://[a-zA-Z0-9-]*\.trycloudflare\.com' cloudflared.log | head -n 1 || true)
        if [ -n "$FOUND" ]; then
            TUNNEL_URL="$FOUND"
            break
        fi
    fi
    sleep 1
done

if [ -z "$TUNNEL_URL" ]; then
    echo "❌ Failed to capture Cloudflare URL. Inspect cloudflared.log:"
    cat cloudflared.log
    exit 1
fi

echo "$TUNNEL_URL" > .live_tunnel_url
WEBHOOK_URL="${TUNNEL_URL}/webhook/vapi-tools"
END_OF_CALL_URL="${TUNNEL_URL}/webhook/vapi-end-of-call"

echo "✅ Cloudflare Tunnel is LIVE!"
echo "   Public Domain : $TUNNEL_URL"
echo "   Server URL    : $WEBHOOK_URL"

# 6. Test Public Tunnel
echo "🧪 Testing public HTTPS tunnel connectivity..."
sleep 2
TEST_RESP=$(curl -sf "${TUNNEL_URL}/health" || echo "FAIL")
if [ "$TEST_RESP" != "FAIL" ]; then
    echo "✅ Public Endpoint Verified: $TEST_RESP"
else
    echo "⚠️ Warning: Tunnel might take a few more seconds to propagate globally."
fi

# 7. Update assistant_config.json with the live URL
"$SCRIPT_DIR/.venv/bin/python" - <<PYEOF
import json
from pathlib import Path

config_path = Path("vapi/assistant_config.json")
if config_path.exists():
    with open(config_path, "r") as f:
        data = json.load(f)
    
    data["serverUrl"] = "${WEBHOOK_URL}"
    # Update tools server url
    for tool in data.get("model", {}).get("tools", []):
        tool["server"] = {"url": "${WEBHOOK_URL}"}

    with open(config_path, "w") as f:
        json.dump(data, f, indent=2)
    print("✅ Updated vapi/assistant_config.json with live server URL.")
PYEOF

echo ""
echo "=========================================================="
echo "🎯 ACTION REQUIRED IN VAPI DASHBOARD:"
echo "1. Open: https://dashboard.vapi.ai -> Assistants"
echo "2. Select 'Luxe Salon Voice Receptionist'"
echo "3. In Server URL, paste:"
echo "   👉  $WEBHOOK_URL"
echo ""
echo "Or paste the contents of vapi/assistant_config.json into Vapi."
echo "=========================================================="

