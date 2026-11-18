#!/usr/bin/env bash
# Remembrall Multi-Format State Exporter (POSIX Shell)
# Exports active project state into Changelog, Release Notes, or GitHub Issue commands.

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FORMAT="${1:-changelog}"
OUTPUT="${2:-}"

echo "🔮 Remembrall Exporter: Generating $FORMAT..."

if command -v node >/dev/null 2>&1 && [ -f "$DIR/bin/remembrall.js" ]; then
    if [ -n "$OUTPUT" ]; then
        node "$DIR/bin/remembrall.js" handoff > "$OUTPUT"
        echo "✅ Exported to: $OUTPUT"
    else
        node "$DIR/bin/remembrall.js" handoff
    fi
elif command -v python3 >/dev/null 2>&1 || command -v python >/dev/null 2>&1; then
    PY_CMD="python3"
    command -v python3 >/dev/null 2>&1 || PY_CMD="python"
    if [ -n "$OUTPUT" ]; then
        "$PY_CMD" "$DIR/.agents/skills/remembrall/scripts/remembrall.py" export --format "$FORMAT" --output "$OUTPUT"
        echo "✅ Exported to: $OUTPUT"
    else
        "$PY_CMD" "$DIR/.agents/skills/remembrall/scripts/remembrall.py" export --format "$FORMAT"
    fi
else
    echo "❌ Error: Neither Node.js nor Python runtime found." >&2
    exit 1
fi
