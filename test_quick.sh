#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================================="
echo "⚡ Running Minimal 1-Click Salon Booking Test"
echo "=========================================================="

# 1. Health check
if ! curl -sf http://127.0.0.1:8000/health > /dev/null; then
    echo "⚠️ FastAPI backend is not running on port 8000. Launching..."
    ./start_live_tunnel.sh
fi

# 2. Trigger quick booking test
echo "🚀 Simulating incoming voice appointment booking..."
RESPONSE=$(curl -sf -X POST http://127.0.0.1:8000/test/quick-booking \
  -H "Content-Type: application/json")

echo "✅ Response received from Voice Backend:"
echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"

# 3. Check Google Sheet ID
SHEET_ID=$(grep "GOOGLE_SHEET_ID=" .env | cut -d '=' -f2 | tr -d ' "' || true)
if [ -n "$SHEET_ID" ] && [ "$SHEET_ID" != "your_google_spreadsheet_id_here" ]; then
    echo ""
    echo "📊 Live Google Sheet Synced:"
    echo "   👉 https://docs.google.com/spreadsheets/d/${SHEET_ID}"
fi

echo ""
echo "📈 View in White-Label Command Center:"
echo "   Run: ./run_admin_portal.sh -> http://localhost:8501"
echo "=========================================================="

