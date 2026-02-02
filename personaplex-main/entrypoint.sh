#!/bin/bash
set -e

# 1. Code Sync
# We rely on 'Baked Images' now. Code is updated during GitHub build.
echo "ℹ️ Using baked-in code (Commit: $(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')). Skipping runtime pull for reliability."

# 2. Start Server
echo "🚀 Starting PersonaPlex Server..."
# The server automatically uses nvidia/personaplex-7b-v1 from the HF cache
exec python3 -m moshi.server \
    --host 0.0.0.0 \
    --port 8998
