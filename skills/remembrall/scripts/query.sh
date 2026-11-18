#!/usr/bin/env bash
# Remembrall Fast Keyword Query Script
# Searches .remembrall.md for features or invariants matching search terms.

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
MANIFEST="${DIR}/.remembrall.md"
QUERY="$*"

if [ -z "$QUERY" ]; then
    echo "Usage: bash query.sh <terms>" >&2
    exit 1
fi

if [ ! -f "$MANIFEST" ]; then
    echo "❌ Manifest not found at: $MANIFEST" >&2
    exit 1
fi

echo "🔍 Searching Remembrall manifest for: '$QUERY'"
grep -i --color=auto "$QUERY" "$MANIFEST" || echo "   (No direct matches found in manifest)"
