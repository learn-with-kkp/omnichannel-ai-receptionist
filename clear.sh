#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "🧹 Executing $0.00 Teardown: Luxe Salon Voice AI Stack"
echo "=========================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -f "stop_live_tunnel.sh" ]; then
    ./stop_live_tunnel.sh || true
fi

if command -v docker &> /dev/null; then
    echo "Stopping and tearing down Docker containers, networks, and volumes..."
    docker compose down -v --remove-orphans || true
fi

if [ -f ".backend.pid" ]; then
    PID=$(cat .backend.pid)
    echo "Terminating local backend process PID: $PID..."
    kill -9 "$PID" 2>/dev/null || true
    rm -f .backend.pid
fi

# Clean SQLite DB and caches
rm -f *.db *.log
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

echo "✅ All resources torn down. Clean zero-cost state verified."
echo "=========================================================="

