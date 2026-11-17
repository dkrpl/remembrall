# Changelog
All notable changes to this project are documented automatically via Remembrall.

## [1.0.0] - 2026-11-18
### Added
- **Remembrall Design Spec** (`docs/superpowers/specs/2026-11-17-remembrall-design.md`) - Spesifikasi kombinasi 3 arsitektur
- **Remembrall Implementation Plan** (`docs/superpowers/plans/2026-11-17-remembrall.md`) - Rencana kerja bertahap TDD
- **Remembrall Template Manifest** (`.remembrall.md`) - Template aktif manifest status proyek
- **Remembrall Skill Definition** (`.agents/skills/remembrall/SKILL.md`) - SOP memori, pruning, dan sync
- **Remembrall Always-On Rule** (`.agents/rules/remembrall.md`) - Pemicu otomatis pre-flight & post-flight
- **Remembrall World-Class Upgrade** (`.agents/skills/remembrall/, README.md, plugin.json`) - Upgrade CLI helper, templates, references & README
- **Remembrall Search & Query Engine** (`.agents/skills/remembrall/scripts/remembrall.py`) - Fast keyword & token weighted search
- **Remembrall MCP Server Engine** (`.agents/skills/remembrall/scripts/mcp_server.py, mcp_config.json`) - Model Context Protocol JSON-RPC server
- **Git & Lifecycle Hooks Automation** (`hooks/, hooks.json`) - Auto-sync pre-commit and Antigravity hooks
- **Standard Python Packaging** (`pyproject.toml, remembrall.cmd, src/remembrall/`) - Pip packageable CLI and global wrappers
- **Multi-OS CI/CD Pipeline** (`.github/workflows/ci.yml`) - GitHub Actions multi-platform matrix tests
- **Interactive Local Web Dashboard** (`.agents/skills/remembrall/scripts/dashboard.py`) - Zero-dependency dark-mode web UI on :4242
- **Semantic Concept Search Engine** (`.agents/skills/remembrall/scripts/semantic.py`) - TF-IDF & Concept Vector cosine matching
- **Multi-Format Exporter** (`.agents/skills/remembrall/scripts/exporter.py`) - Changelog, GitHub Issues, Release Notes
- **Zero-Amnesia Simulation Engine** (`.agents/skills/remembrall/scripts/simulation.py`) - Benchmark instant recall vs blind scan
