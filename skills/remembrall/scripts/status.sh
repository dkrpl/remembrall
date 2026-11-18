#!/usr/bin/env bash
# Remembrall Status Helper Script
# Prints the current manifest status, line budget, and completion rate.

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
MANIFEST="${DIR}/.remembrall.md"

if [ ! -f "$MANIFEST" ]; then
    echo "❌ [Remembrall]: No .remembrall.md manifest found in $DIR" >&2
    exit 1
fi

TOTAL_LINES=$(wc -l < "$MANIFEST")
DONE_COUNT=$(grep -c "DONE" "$MANIFEST" || true)
WIP_COUNT=$(grep -c "WIP" "$MANIFEST" || true)
PLANNED_COUNT=$(grep -c "PLANNED" "$MANIFEST" || true)

echo "🔮 [Remembrall State Monitor]"
echo "   Manifest: $MANIFEST"
echo "   Line Budget: $TOTAL_LINES / 120 lines"
echo "   Features: $DONE_COUNT Completed | $WIP_COUNT In Progress | $PLANNED_COUNT Planned"

if [ "$TOTAL_LINES" -gt 120 ]; then
    echo "⚠️ WARNING: Manifest has exceeded the 120-line ceiling! Run 'remembrall prune'." >&2
fi
