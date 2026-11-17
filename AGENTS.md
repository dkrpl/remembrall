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
