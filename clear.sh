#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "🧹 Omnichannel Voice AI Receptionist: \$0.00 Teardown"
echo "=========================================================="

# 1. Kill local uvicorn and background services
echo "🛑 Terminating local processes..."
pkill -f "uvicorn backend.app:app" || true

# 2. Clean temporary caches, bytecode, and logs
echo "🗑️ Removing pycache, test artifacts, and logs..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
rm -rf .coverage htmlcov 2>/dev/null || true

# 3. Stop Docker containers if running
if command -v docker-compose &> /dev/null; then
  echo "🐳 Tearing down docker containers..."
  docker-compose down -v --remove-orphans || true
fi

echo "=========================================================="
echo "✨ Local environment clean. Teardown cost: \$0.00."
echo "=========================================================="
