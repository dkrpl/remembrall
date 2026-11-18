#!/usr/bin/env bash
# Remembrall State Synchronization Helper
# Ensures working directory changes are recorded in .remembrall.md before committing.

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"

echo "🔮 Checking state synchronization between Git and Remembrall..."

MODIFIED_FILES=$(git status --porcelain | awk '{print $2}')

if [ -z "$MODIFIED_FILES" ]; then
    echo "✨ Working tree clean. State is synchronized."
    exit 0
fi

echo "📝 Currently modified/untracked files:"
echo "$MODIFIED_FILES" | sed 's/^/   - /'

if [ -f ".remembrall.md" ]; then
    echo ""
    echo "🔍 Verifying .remembrall.md records..."
    if command -v node >/dev/null 2>&1 && [ -f "bin/remembrall.js" ]; then
        node bin/remembrall.js status
    else
        python .agents/skills/remembrall/scripts/remembrall.py status
    fi
fi
