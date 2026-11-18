#!/usr/bin/env bash
# Remembrall Git Commit Auto-Capture
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

node "$DIR/bin/remembrall.js" capture "$@"
