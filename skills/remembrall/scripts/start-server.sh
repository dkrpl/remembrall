#!/usr/bin/env bash
# Start Web Dashboard Companion (Superpowers Pattern)
PORT="${1:-4242}"

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

echo "🔮 Starting Remembrall Visual Companion on http://localhost:$PORT..."

if command -v node >/dev/null 2>&1 && [ -f "$DIR/bin/remembrall.js" ]; then
    node "$DIR/bin/remembrall.js" ui --port "$PORT"
elif command -v python3 >/dev/null 2>&1; then
    python3 "$DIR/.agents/skills/remembrall/scripts/dashboard.py" --port "$PORT"
else
    python "$DIR/.agents/skills/remembrall/scripts/dashboard.py" --port "$PORT"
fi
