#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "🚀 Omnichannel Voice AI Receptionist: Enterprise Deploy"
echo "=========================================================="

# 1. Environment check
if [ ! -f .env ]; then
  echo "⚠️ .env file not found. Copying from .env.example..."
  cp .env.example .env
fi

# 2. Run test verification (78 tests)
echo "🧪 Running full test suite pre-flight check..."
PYTHONPATH=. pytest tests/ -q

# 3. Deploy to Vercel Production
echo "🌐 Deploying to Vercel Production..."
vercel --prod --yes

echo "=========================================================="
echo "✅ Deployment Successful!"
echo "Production URL: https://ai-voice-receptionist.kishor.tech/"
echo "Vapi Web SDK Studio: https://ai-voice-receptionist.kishor.tech/vapi-call"
echo "=========================================================="
