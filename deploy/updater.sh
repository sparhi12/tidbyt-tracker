#!/usr/bin/env bash
# ==============================================================================
# Tidbyt Flight Tracker - Headless GitHub Auto-Updater
# Checks origin/main every 3 minutes. Pulls updates and restarts daemon.
# ==============================================================================
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$APP_DIR"

# Ensure we are inside a git repository
if [ ! -d ".git" ]; then
    exit 0
fi

# Fetch remote changes silently
git fetch origin main --quiet 2>/dev/null || exit 0

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main 2>/dev/null || echo "$LOCAL")

if [ "$LOCAL" != "$REMOTE" ]; then
    echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] New commit detected on origin/main. Updating ($LOCAL -> $REMOTE)..."
    git pull origin main --quiet

    # Reinstall Python requirements if requirements.txt changed
    if git diff --name-only "$LOCAL" "$REMOTE" | grep -q "requirements.txt"; then
        echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] requirements.txt updated. Reinstalling..."
        "$APP_DIR/venv/bin/pip" install -q -r requirements.txt
    fi

    # Restart daemon service
    echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] Restarting tidbyt-tracker service..."
    sudo systemctl restart tidbyt-tracker.service || true
    echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] Update successfully applied."
fi
