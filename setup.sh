#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================================="
echo "💈 Setting Up Luxe Salon AI Voice Receptionist"
echo "=========================================================="

# 1. Initialize .env if missing
if [ ! -f ".env" ]; then
    echo "📄 Creating .env from .env.example..."
    cp .env.example .env
    echo "👉 Please edit .env with your VAPI_API_KEY and TWILIO credentials."
fi

# 2. Virtual Environment Setup
if [ ! -d ".venv" ]; then
    echo "🐍 Creating dedicated Python virtual environment..."
    python3 -m venv .venv
fi

echo "📦 Installing production dependencies..."
.venv/bin/pip install --upgrade pip -q
.venv/bin/pip install -r requirements.txt -q

# 3. Check cloudflared
if ! command -v cloudflared &> /dev/null; then
    echo "⚠️ Cloudflared not found. On macOS, run: brew install cloudflared"
fi

# 4. Run Self-Diagnostics Test Suite
echo "🧪 Running self-diagnostic tests..."
.venv/bin/pytest tests/ -q

echo "=========================================================="
echo "✅ Setup Complete! Ready for Production."
echo ""
echo "🚀 Quick Start Commands:"
echo "1. Start Voice Backend + Public Tunnel :"
echo "   ./start_live_tunnel.sh"
echo ""
echo "2. Launch White-Label Command Center   :"
echo "   ./run_admin_portal.sh"
echo ""
echo "3. Onboard a New Paying Salon Client   :"
echo "   python3 scripts/onboard_new_salon.py --name 'Salon Name' --phone '+1234567890'"
echo "=========================================================="

