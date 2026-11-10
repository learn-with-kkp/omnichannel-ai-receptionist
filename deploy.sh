#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "🚀 Deploying Luxe Salon Voice AI Receptionist (Vapi + n8n)"
echo "=========================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Environment Verification
if ! command -v docker &> /dev/null; then
    echo "⚠️ Docker not detected. Falling back to local Python background runner..."
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
    fi
    source .venv/bin/activate
    pip install -q -r requirements.txt
    python3 -m pytest tests/ -q
    nohup uvicorn backend.app:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
    echo $! > .backend.pid
    echo "✅ FastAPI Backend running in background on port 8000 (PID: $(cat .backend.pid))"
else
    echo "🐳 Starting multi-container stack via Docker Compose..."
    docker compose up -d --build
    echo "✅ Stack launched successfully!"
    echo "   - FastAPI Webhook Server: http://localhost:8000"
    echo "   - n8n Automation Engine : http://localhost:5678"
fi

echo ""
echo "📞 Vapi Assistant Configuration Ready:"
echo "   File: $SCRIPT_DIR/vapi/assistant_config.json"
echo "   Import into https://dashboard.vapi.ai -> Assistants"
echo "=========================================================="

