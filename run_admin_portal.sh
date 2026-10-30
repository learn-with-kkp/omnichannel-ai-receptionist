#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================================="
echo "💇‍♀️ Starting Luxe Salon Voice AI - White-Label Command Center"
echo "=========================================================="

"$SCRIPT_DIR/.venv/bin/streamlit" run admin_portal.py --server.port 8501 --server.headless true

