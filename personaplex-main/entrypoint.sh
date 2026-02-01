#!/bin/bash
set -e

# 1. Code Sync (The "Update" Feature)
# Pull latest code from the PUBLIC repo (no auth needed)
if [ -d ".git" ]; then
    echo "🔍 Checking for updates from GitHub..."
    # Force non-interactive mode and use public HTTPS URL
    git config --global credential.helper ""
    git pull --no-rebase https://github.com/Matthew-Kode/English.git main 2>/dev/null || echo "⚠️ Git pull failed, using baked-in code."
else
    echo "ℹ️ Not a git repo (Snapshot mode). Skipping git pull."
fi

# 2. Start Server
echo "🚀 Starting PersonaPlex Server..."
# The server automatically uses nvidia/personaplex-7b-v1 from the HF cache
exec python3 -m moshi.server \
    --host 0.0.0.0 \
    --port 8998
