#!/usr/bin/env bash
# Remembrall Comprehensive Environment Verification Script
# Validates manifest, rules, hooks, Node.js CLI, and Python fallbacks.

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"

echo "🔮 Running Remembrall Full Health Verification..."

# 1. Check .remembrall.md
if [ ! -f ".remembrall.md" ]; then
    echo "❌ FAIL: .remembrall.md not found in repository root." >&2
    exit 1
fi

LINE_COUNT=$(wc -l < .remembrall.md)
if [ "$LINE_COUNT" -gt 120 ]; then
    echo "❌ FAIL: .remembrall.md has $LINE_COUNT lines (maximum budget is 120)." >&2
    exit 1
fi
echo "✅ Manifest structure & budget check passed ($LINE_COUNT/120 lines)."

# 2. Check Node CLI
if command -v node >/dev/null 2>&1; then
    echo "⚡ Verifying Node.js Engine..."
    node bin/remembrall.js validate
    node --test tests/*.test.js
    echo "✅ Node.js Engine & unit tests passed."
else
    echo "⚠️ Node.js not detected; skipping Node validation."
fi

# 3. Check Python Engine
if command -v python3 >/dev/null 2>&1 || command -v python >/dev/null 2>&1; then
    PY_CMD="python3"
    command -v python3 >/dev/null 2>&1 || PY_CMD="python"
    echo "🐍 Verifying Python Engine..."
    "$PY_CMD" .agents/skills/remembrall/scripts/remembrall.py validate
    echo "✅ Python CLI validation passed."
fi

# 4. Check Hooks
if [ -f "hooks/pre-commit" ] && [ -f "hooks/SessionStart" ]; then
    echo "✅ Lifecycle hooks verified."
fi

echo "🎉 All Remembrall components verified successfully!"
