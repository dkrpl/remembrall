#!/usr/bin/env bash
# Remembrall Empirical Simulation Benchmark (POSIX Shell)
# Evaluates token consumption of zero-amnesia recalls versus brute-force scanning.

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TURNS="${1:-20}"

echo "🔮 Running Remembrall Zero-Amnesia Token Benchmark ($TURNS turns)..."

if command -v python3 >/dev/null 2>&1 || command -v python >/dev/null 2>&1; then
    PY_CMD="python3"
    command -v python3 >/dev/null 2>&1 || PY_CMD="python"
    "$PY_CMD" "$DIR/.agents/skills/remembrall/scripts/remembrall.py" simulate --turns "$TURNS"
else
    echo "⚠️ Python required for empirical token simulation."
fi
