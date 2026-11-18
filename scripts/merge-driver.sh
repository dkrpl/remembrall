#!/usr/bin/env bash
# Remembrall 3-Way Semantic Merge Driver for Git
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

if command -v node >/dev/null 2>&1; then
    exec node "${ROOT_DIR}/bin/remembrall.js" merge-driver "$@"
else
    echo "Node.js required for Remembrall merge driver." >&2
    exit 1
fi
