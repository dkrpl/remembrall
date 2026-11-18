#!/usr/bin/env bash
# Remembrall Project Setup Wizard (Linux / macOS / Git Bash)
# Bootstraps .remembrall.md, sets up agent rules, and installs git hooks.

set -e

TARGET_DIR="${1:-.}"
cd "$TARGET_DIR"

echo "🔮 Initializing Remembrall in $(pwd)..."

# 1. Create .remembrall.md if not exists
if [ ! -f ".remembrall.md" ]; then
    PROJECT_NAME=$(basename "$(pwd)")
    cat <<EOF > .remembrall.md
# Project Overview
- **Project:** $PROJECT_NAME
- **Stack:** Auto-detected repository
- **Purpose:** Persistent memory and zero-rescan feature tracking.

---

## Feature Manifest
| ID | Fitur | Status | File Terkait | Catatan |
|---|---|---|---|---|
| F-001 | Initial Bootstrap | DONE | .remembrall.md | Manifest initialized |

---

## Technical Findings
- **Zero Re-scan:** Check this file before scanning codebase directories.
- **Max Budget:** Strictly keep under 120 lines.
EOF
    echo "✅ Created .remembrall.md"
else
    echo "ℹ️  .remembrall.md already exists."
fi

# 2. Setup AGENTS.md rule
if [ ! -f "AGENTS.md" ]; then
    cat <<'EOF' > AGENTS.md
# Remembrall Protocol (Universal Agent Memory)

All AI agents (Claude, Cursor, Devin, Codex, Copilot, Antigravity) working in this workspace must follow this protocol:

1. **Pre-flight Check (Zero Re-scan):**
   - Check `.remembrall.md` before performing broad workspace scans or recursive searches.
   - If the requested feature or component is already listed, inspect only its associated files directly.

2. **Post-flight Hard Gate (State Sync):**
   - Before reporting a task or feature as complete, update `.remembrall.md`:
     - Mark status as `DONE`.
     - Ensure touched files and a 1-line note are present in the table.
     - Prune lines if the file approaches 100 lines.
   - Never finalize a task with undocumented changes.
EOF
    echo "✅ Created AGENTS.md"
fi

# 3. Install Git pre-commit hook if in a git repo
if [ -d ".git" ]; then
    mkdir -p .git/hooks
    HOOK_TARGET=".git/hooks/pre-commit"
    cat <<'EOF' > "$HOOK_TARGET"
#!/bin/sh
if [ -f ".remembrall.md" ]; then
    LINES=$(wc -l < .remembrall.md)
    if [ "$LINES" -gt 120 ]; then
        echo "❌ Commit rejected: .remembrall.md has $LINES lines (limit: 120)."
        echo "   Please consolidate features before committing."
        exit 1
    fi
fi
exit 0
EOF
    chmod +x "$HOOK_TARGET"
    echo "✅ Installed .git/hooks/pre-commit"
fi

echo "🎉 Remembrall workspace setup complete!"
