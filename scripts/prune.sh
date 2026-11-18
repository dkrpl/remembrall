#!/usr/bin/env bash
# Remembrall Anti-Bloat Consolidation Script (POSIX Shell)
# Compresses older historical DONE features when approaching line budget.

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="${DIR}/.remembrall.md"

if [ ! -f "$MANIFEST" ]; then
    echo "❌ [Remembrall]: Manifest not found at: $MANIFEST" >&2
    exit 1
fi

LINE_COUNT=$(wc -l < "$MANIFEST")
echo "🔮 Remembrall Anti-Bloat Engine (Current: $LINE_COUNT/120 lines)..."

if command -v node >/dev/null 2>&1 && [ -f "$DIR/bin/remembrall.js" ]; then
    node "$DIR/bin/remembrall.js" prune
elif command -v python3 >/dev/null 2>&1 || command -v python >/dev/null 2>&1; then
    PY_CMD="python3"
    command -v python3 >/dev/null 2>&1 || PY_CMD="python"
    "$PY_CMD" "$DIR/.agents/skills/remembrall/scripts/remembrall.py" prune
else
    echo "❌ Error: Neither Node.js nor Python runtime found." >&2
    exit 1
fi

NEW_COUNT=$(wc -l < "$MANIFEST")
echo "✅ Prune completed. New manifest line budget: $NEW_COUNT/120 lines."
