#!/usr/bin/env bash
# Remembrall Task-Gate Helper (Superpowers SDD Pattern)
# Ensures task is recorded and .remembrall.md is valid before concluding a turn.

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
MANIFEST="${DIR}/.remembrall.md"

if [ ! -f "$MANIFEST" ]; then
    echo "❌ Post-flight Gate Rejected: .remembrall.md not found!" >&2
    exit 1
fi

LINE_COUNT=$(wc -l < "$MANIFEST")
if [ "$LINE_COUNT" -gt 120 ]; then
    echo "❌ Post-flight Gate Rejected: .remembrall.md has $LINE_COUNT lines (ceiling: 120)." >&2
    echo "   Action required: Prune or consolidate features before finalizing." >&2
    exit 1
fi

echo "✅ Remembrall Post-Flight Gate PASSED: State manifest healthy ($LINE_COUNT/120 lines)."
