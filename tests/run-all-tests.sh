#!/usr/bin/env bash
# POSIX Test Suite Runner for Remembrall
set -e

echo "=== RUNNING REMEMBRALL POSIX TEST SUITE ==="

# 1. Manifest structural check
if [ -f ".remembrall.md" ]; then
    LINES=$(wc -l < .remembrall.md)
    if [ "$LINES" -gt 120 ]; then
        echo "❌ FAIL: .remembrall.md has $LINES lines (> 120)."
        exit 1
    fi
    echo "✅ .remembrall.md line budget passed ($LINES lines)."
fi

# 2. Node.js unit tests
if command -v node >/dev/null 2>&1; then
    echo "Running Node.js tests..."
    node --test tests/*.test.js
    echo "✅ Node.js tests passed."
fi

# 3. Python unit tests
if command -v python3 >/dev/null 2>&1; then
    echo "Running Python tests..."
    python3 -m unittest discover -s tests -p "test_*.py" -v
    echo "✅ Python tests passed."
elif command -v python >/dev/null 2>&1; then
    echo "Running Python tests..."
    python -m unittest discover -s tests -p "test_*.py" -v
    echo "✅ Python tests passed."
fi

# 4. CLI Validation
if command -v node >/dev/null 2>&1 && [ -f "bin/remembrall.js" ]; then
    node bin/remembrall.js validate
fi

echo "=== ALL TESTS PASSED SUCCESSFULLY! ==="
