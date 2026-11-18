#!/usr/bin/env bash
# Remembrall Dashboard Launcher
PORT="${1:-4242}"

echo "🔮 Launching Remembrall Dark-Mode Dashboard on http://localhost:$PORT..."

if command -v node >/dev/null 2>&1 && [ -f "bin/remembrall.js" ]; then
    node bin/remembrall.js ui --port "$PORT"
elif command -v python3 >/dev/null 2>&1; then
    python3 .agents/skills/remembrall/scripts/dashboard.py --port "$PORT"
else
    python .agents/skills/remembrall/scripts/dashboard.py --port "$PORT"
fi
