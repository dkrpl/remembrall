#!/usr/bin/env bash
# Remembrall Gatekeeper Enforcement
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

if command -v node >/dev/null 2>&1; then
    exec node "${ROOT_DIR}/bin/remembrall.js" gatekeeper "$@"
elif command -v python3 >/dev/null 2>&1; then
    exec python3 "${ROOT_DIR}/.agents/skills/remembrall/scripts/remembrall.py" validate
else
    echo "Node.js or Python required for Remembrall gatekeeper." >&2
    exit 1
fi
