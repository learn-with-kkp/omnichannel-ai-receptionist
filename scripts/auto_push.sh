#!/bin/bash
# ==============================================================================
# 🚀 Learn-With-KKP Automated Double-Push Script
# Pushes the master repository and triggers instantaneous shielded synchronization
# to https://github.com/learn-with-kkp/omnichannel-ai-receptionist
# ==============================================================================

set -e

MSG="${1:-feat: update omnichannel architecture and voice agents}"
BRANCH="$(git rev-parse --abbrev-ref HEAD)"

echo "📦 [1/3] Adding changes in master repository ($BRANCH)..."
git add -A

if git diff-index --quiet HEAD --; then
    echo "ℹ️  No changes to commit in master repository."
else
    git commit -m "$MSG"
fi

echo "🚀 [2/3] Pushing $BRANCH to master remote (KishorKumarParoi/omnichannel-voice-chat-ai-receptionist)..."
git push origin "$BRANCH"

echo "🛡️  [3/3] Running multi-layer cipher shield & syncing to learn-with-kkp/omnichannel-ai-receptionist ($BRANCH)..."
python3 scripts/sync_to_learn_with_kkp.py --branch "$BRANCH" --message "$MSG"

echo "🎉 DOUBLE-PUSH COMPLETED SUCCESSFULLY!"
echo "Master: https://github.com/KishorKumarParoi/omnichannel-voice-chat-ai-receptionist (branch: $BRANCH)"
echo "Shielded Public: https://github.com/learn-with-kkp/omnichannel-ai-receptionist (branch: $BRANCH)"
