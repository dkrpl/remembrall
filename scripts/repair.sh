#!/usr/bin/env bash
# Remembrall Self-Healing Auto-Repair
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

if command -v node >/dev/null 2>&1; then
    exec node "${ROOT_DIR}/bin/remembrall.js" repair "$@"
else
    echo "Node.js required for Remembrall auto-repair." >&2
    exit 1
fi
