---
name: remembrall-setup
description: Use when onboarding a new or existing repository to Remembrall persistent memory, configuring rules, and installing automated pre-commit gates
---

# Remembrall Setup (Interactive Onboarding)

> **Spine Skill inspired by Matt Pocock's `/setup-...` workflow.**  
> Automatically detects repository stack, scaffolds `.remembrall.md`, configures always-on rules, and attaches pre-commit verification hooks.

## Onboarding Procedure

When running `/remembrall-setup` or onboarding a project:

1. **Detect Workspace Stack:**
   - Look for `package.json` -> Web/Node template.
   - Look for `pyproject.toml` or `requirements.txt` -> REST API/Python template.
   - Look for `Cargo.toml` or `go.mod` -> Systems/Backend template.
   - Default -> Minimal template.

2. **Scaffold Manifest:**
   Run CLI scaffolding command:
   ```bash
   remembrall init --template [auto-detected]
   ```

3. **Install Git Pre-Commit Hook:**
   Run hook installer:
   ```bash
   remembrall install-hooks
   ```

4. **Verify Health:**
   ```bash
   remembrall status
   ```
   Confirm to user: *"Remembrall successfully configured for this repository. Zero-amnesia tracking is now active."*
