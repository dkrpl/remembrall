#!/usr/bin/env bash
# Remembrall Mermaid Diagram Generator
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FORMAT="${1:-flowchart}"

node "$DIR/bin/remembrall.js" diagram --format "$FORMAT"
