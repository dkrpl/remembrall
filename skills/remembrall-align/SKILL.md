---
name: remembrall-align
description: Use before transitioning any feature from PLANNED to WIP to run Socratic invariant verification questions (Jane Street style)
---

# 🧙‍♂️ Remembrall Socratic Alignment Protocol

Use this skill whenever you are about to begin work on a new feature or task.

## When to Use
- Before moving any feature status from `PLANNED` to `WIP`.
- Before writing implementation code on an existing codebase.
- To prevent architectural regressions and non-goal scope creep.

## Execution Workflow
1. Run alignment check on the feature:
   ```bash
   remembrall align <FEATURE_ID>
   ```
2. Answer the diagnostic questions in your reasoning turn:
   - **Invariant Check:** Does this implementation comply with the architectural invariants in `## Technical Findings`?
   - **Non-Goals:** What files or existing modules must NOT be modified?
   - **Evidence Command:** What test or command will prove completion before setting status to `DONE`?
3. Transition feature to `WIP`:
   ```bash
   remembrall set <FEATURE_ID> WIP --note "Starting implementation with verified invariants"
   ```
