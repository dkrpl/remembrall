#!/usr/bin/env bash
# Remembrall Setup Sub-Skill Runner (Matt Pocock & Superpowers Spine)
# Scaffolds fresh .remembrall.md and configures agent rules.

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
TARGET="${1:-$DIR}"

echo "🔮 [remembrall-setup]: Initializing memory scaffold in $TARGET..."
bash "$DIR/scripts/setup-agent.sh" "$TARGET"
