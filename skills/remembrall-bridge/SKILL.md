---
name: remembrall-bridge
description: Use when transitioning a project session across different AI coding agents (Claude Code, Cursor, Codex, Antigravity) without losing state
---

# 🌉 Universal Cross-Agent Memory Bridge

Use this skill when handing off the current project state between different AI environments.

## Supported Agents
- `cursor`: Generates `.cursorrules` and active composer context.
- `claude`: Generates XML-structured `<remembrall_memory>` system prompt blocks.
- `codex`: Generates concise task context for OpenAI Codex.
- `antigravity`: Generates Google Antigravity protocol brief.

## Execution Workflow
1. Ensure working tree is synchronized:
   ```bash
   remembrall sync
   ```
2. Generate target bridge format:
   ```bash
   remembrall bridge --target cursor
   remembrall bridge --target claude
   ```
3. Paste or inject the output into the target agent environment.
