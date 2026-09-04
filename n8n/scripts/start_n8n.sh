#!/usr/bin/env bash
# ============================================================
# MarketVoice SEA — Launch n8n Locally (Unix/Mac/WSL)
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
N8N_DIR="$(dirname "$SCRIPT_DIR")"
cd "$N8N_DIR"

echo "============================================================"
echo "  MarketVoice SEA — n8n Local Workflow Orchestrator"
echo "============================================================"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js is not installed or not in PATH."
    exit 1
fi

echo "[OK] Node.js version: $(node -v)"

# Load .env
if [ -f "$N8N_DIR/.env" ]; then
    echo "[OK] Loading environment configuration from .env"
    set -a
    source "$N8N_DIR/.env"
    set +a
fi

# Ensure data dir
mkdir -p "$N8N_DIR/data"
export N8N_USER_FOLDER="$N8N_DIR/data"

echo ""
echo ">> Starting n8n server on http://localhost:5678 ..."
echo ">> Press Ctrl+C to stop the server."
echo ""

npx n8n start --port 5678
