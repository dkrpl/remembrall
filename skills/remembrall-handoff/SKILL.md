---
name: remembrall-handoff
description: Use when transitioning work between agents, switching conversation sessions, or passing state to a fresh subagent without losing context
---

# Remembrall Handoff (Agent-to-Agent State Transition)

> **Spine Skill inspired by Matt Pocock's `/handoff` workflow.**  
> Serializes project state, active WIP tasks, and key invariants into an ultra-dense, token-optimized briefing block.

## Handoff Procedure

When transitioning to a new session or subagent:

1. **Serialize Active State:**
   Execute the handoff generator:
   ```bash
   remembrall handoff
   ```

2. **Handoff Block Format:**
   The generator produces an unambiguous briefing block:
   ```markdown
   === REMEMBRALL SESSION HANDOFF BRIEF ===
   Project: [Project Name]
   Active State: [N] features total, [X] DONE, [Y] WIP
   Current Task: [ID] [Feature Name] ([Files])
   Invariants: [Key technical constraints from .remembrall.md]
   Next Steps: [Immediate action items]
   ========================================
   ```

3. **Next Agent Action:**
   The receiving agent reads the handoff block, skips recursive directory scanning, and starts work directly on the listed `Current Task`.
