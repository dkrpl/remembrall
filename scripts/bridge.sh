#!/usr/bin/env bash
# Remembrall Cross-Agent Bridge Runner
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_AGENT="${1:-cursor}"

node "$DIR/bin/remembrall.js" bridge --target "$TARGET_AGENT"
