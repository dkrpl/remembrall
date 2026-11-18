---
trigger: always_on
description: Ensures agent checks project state before searching files and updates feature status upon task completion
---

# Remembrall Protocol (State & Memory Enforcement)

1. **Pre-flight Check (Zero Re-scan):**
   - At the beginning of any task or query regarding existing features, inspect `.remembrall.md` before performing broad workspace scans (`read_file .remembrall.md`).
   - If the requested feature or component is already documented, inspect only its listed files directly.
   - If not found in the active manifest, query two-tier memory via `remembrall query <term>` or inspect `.remembrall.archive.md` before scanning the repo.

2. **Post-flight Hard Gate (State Sync):**
   - Before reporting a task or feature as complete, update `.remembrall.md`:
     - Mark status as `DONE`.
     - Ensure touched files and a 1-line note are present in the table.
     - Prune lines if the file approaches 100 lines per the `remembrall` skill.
   - Never finalize a task with undocumented changes.
