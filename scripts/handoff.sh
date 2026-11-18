#!/usr/bin/env bash
# Remembrall Instant Session Handoff Generator (POSIX Shell)
# Generates concise context briefs for transitioning between AI agents or sessions.

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="${DIR}/.remembrall.md"

if [ ! -f "$MANIFEST" ]; then
    echo "❌ Manifest not found at: $MANIFEST" >&2
    exit 1
fi

if command -v node >/dev/null 2>&1 && [ -f "$DIR/bin/remembrall.js" ]; then
    node "$DIR/bin/remembrall.js" handoff
elif command -v python3 >/dev/null 2>&1 || command -v python >/dev/null 2>&1; then
    PY_CMD="python3"
    command -v python3 >/dev/null 2>&1 || PY_CMD="python"
    "$PY_CMD" "$DIR/.agents/skills/remembrall/scripts/remembrall.py" handoff
else
    echo "❌ Error: Neither Node.js nor Python runtime found." >&2
    exit 1
fi
