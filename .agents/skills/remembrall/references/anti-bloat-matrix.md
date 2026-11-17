# Remembrall Anti-Bloat Matrix

To keep `.remembrall.md` under 120 lines and ensure lightning-fast agent reads, follow this strict categorization matrix:

| Content Type | Belongs in `.remembrall.md`? | Where It Belongs Instead |
|---|---|---|
| **Feature Status (`DONE`, `WIP`, `PLANNED`)** | ✅ **YES** | Feature Manifest Table |
| **Primary File Links (`src/auth.ts`)** | ✅ **YES** | Feature Manifest Table |
| **1-Line High-Level Outcome** | ✅ **YES** | Feature Manifest Table (Notes column) |
| **Key Architectural Invariants (max 5)** | ✅ **YES** | `## Technical Findings` |
| **Full Step-by-Step Implementation Plans** | ❌ **NO** | `docs/plans/` or issue tracker |
| **Full Architecture Design Documents** | ❌ **NO** | `docs/specs/` |
| **Code Snippets or Refactoring Diffs** | ❌ **NO** | Source code & Git commits |
| **Debugging Transcripts / Terminal Output** | ❌ **NO** | Terminal logs / scratchpad |
| **Chat History / User Instructions** | ❌ **NO** | Ephemeral conversation context |

## Pruning Rules
1. **The 100-Line Alarm:** If `.remembrall.md` reaches 100 lines, immediately execute `python .agents/skills/remembrall/scripts/remembrall.py prune`.
2. **Consolidation:** 5 to 10 historical `DONE` features collapse into a single row (`| F-001..F-008 | Core Foundations | DONE | ... | Stabilized |`).
3. **Findings Garbage Collection:** Remove temporary findings that are no longer active gotchas.
