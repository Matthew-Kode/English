#!/bin/bash
set -e

# 1. Code Sync (The "Update" Feature)
# If this container was built from an older commit, we pull the latest main.
# Note: This requires the container to have git credentials or be a public repo.
if [ -d ".git" ]; then
    echo "🔍 Checking for updates from GitHub..."
    git pull origin main || echo "⚠️ Git pull failed (Auth issue?), skipping update."
else
    echo "ℹ️ Not a git repo (Snapshot mode). Skipping git pull."
fi

# 2. Start Server
echo "🚀 Starting PersonaPlex Server..."
# We use the baked-in model names
exec python3 -m moshi.server \
    --host 0.0.0.0 \
    --port 8998 \
    --text-tokenizer "nvidia/personaplex-7b-v1" \
    --moshi-weight "nvidia/personaplex-7b-v1"
