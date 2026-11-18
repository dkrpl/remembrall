#!/usr/bin/env bash
# Remembrall Socratic Alignment CLI Runner
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_ID="${1:-}"

if [ -z "$TARGET_ID" ]; then
    echo "Usage: bash scripts/align.sh <FEATURE_ID>" >&2
    exit 1
fi

node "$DIR/bin/remembrall.js" align "$TARGET_ID"
