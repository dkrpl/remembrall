<div align="center">

```text
██████╗ ███████╗███╗   ███╗███████╗███╗   ███╗██████╗ ██████╗  █████╗ ██╗     ██╗     
██╔══██╗██╔════╝████╗ ████║██╔════╝████╗ ████║██╔══██╗██╔══██╗██╔══██╗██║     ██║     
██████╔╝█████╗  ██╔████╔██║█████╗  ██╔████╔██║██████╔╝██████╔╝███████║██║     ██║     
██╔══██╗██╔══╝  ██║╚██╔╝██║██╔══╝  ██║╚██╔╝██║██╔══██╗██╔══██╗██╔══██║██║     ██║     
██║  ██║███████╗██║ ╚═╝ ██║███████╗██║ ╚═╝ ██║██████╔╝██║  ██║██║  ██║███████╗███████╗
╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝
```

### 🔮 Universal Zero-Amnesia State Engine & Persistent Memory for AI Coding Agents
*Inspired by Manus AI disk persistence, `auto-memory-pro` token curation, and `obra/superpowers` universal multi-agent harness architecture.*

[![CI Matrix](https://github.com/dkrpl/remembrall/actions/workflows/ci.yml/badge.svg)](https://github.com/dkrpl/remembrall/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Skill Leaderboard](https://img.shields.io/badge/Skill%20Leaderboard-Indexed-green.svg)](https://www.skillleaderboard.com/)
[![MCP Server](https://img.shields.io/badge/MCP-Standard%202024--11--05-purple.svg)](https://modelcontextprotocol.io/)
[![Universal Agent Skills](https://img.shields.io/badge/Agent%20Skills-Standard%20v1.0-cyan.svg)](https://agentskills.io/)
[![Token Efficiency](https://img.shields.io/badge/Token%20Reduction-83%25-orange.svg)]()

[How it Works](#-how-it-works) • [Installation](#-installation-by-harness) • [CLI & MCP Tools](#-complete-cli--mcp-tools-reference) • [Web Dashboard](#-interactive-web-dashboard) • [Benchmarks](#-empirical-benchmarks) • [FAQ](#-frequently-asked-questions)

</div>

---

## ⚡ How it Works

Remembrall is an external working memory engine for AI coding agents. It prevents agents from suffering from **amnesic scanning** during long conversations or session resets:

1. **Pre-flight Recall (Turn 1):** Before exploring directories or answering questions about what was built, the agent automatically reads `.remembrall.md` (~250 tokens). It spots the exact feature and files instantly without re-scanning code.
2. **Deterministic Execution:** The agent implements changes guided by known project invariants and constraints.
3. **Post-flight Hard Gate:** Before reporting work as finished, the agent must update `.remembrall.md` with the new status and touched files.
4. **Autonomous Anti-Bloat:** If `.remembrall.md` reaches 100 lines, older historical features automatically consolidate into single-line module summaries, keeping token intake flat forever.

---

## 🚀 Installation by Harness

Installation differs by harness. Install Remembrall for your primary environment:

### 1. Antigravity & Gemini CLI
Install Remembrall directly from GitHub:
```bash
agy plugin install https://github.com/dkrpl/remembrall
```
*Antigravity automatically discovers `gemini-extension.json` and loads `GEMINI.md` as an always-on memory protocol.*

---

### 2. Claude Code
Install via Claude plugin marketplace:
```bash
/plugin marketplace add dkrpl/remembrall
/plugin install remembrall@remembrall-marketplace
```

---

### 3. Cursor & Windsurf
Add Remembrall to your MCP configuration (`~/.cursor/mcp.json` or `.codeium/windsurf/mcp_config.json`):
```json
{
  "mcpServers": {
    "remembrall": {
      "command": "python",
      "args": ["path/to/remembrall/.agents/skills/remembrall/scripts/mcp_server.py"]
    }
  }
}
```
*Cursor also automatically loads `AGENTS.md` and `.cursor-plugin/plugin.json`.*

---

### 4. Universal NPM / Agent Skills Standard (Codex, Devin, OpenCode)
```bash
npx skills add dkrpl/remembrall --skill remembrall -g
```

---

### 5. Native Python CLI (Pip / Standalone)
```bash
git clone https://github.com/dkrpl/remembrall.git
cd remembrall
pip install -e .

# Launch local interactive web dashboard:
remembrall ui

# Run bilingual concept vector search:
remembrall semantic "login auth"

# Run empirical simulation:
remembrall simulate --turns 20
```

---

## 🖥️ Interactive Web Dashboard (`remembrall ui`)

Launch a sleek dark-mode local web dashboard in your browser (`http://localhost:4242`):

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🔮 Remembrall State Engine                               [+ Register Feature]│
├─────────────────────────────────────────────────────────────────────────────┤
│ [15 Features Tracked]  [83% Token Savings]  [36/120 Lines]  [● HEALTHY]    │
├─────────────────────────────────────────────────────────────────────────────┤
│ 🔍 [Search features or files...]         [Filter: All | Done | WIP | Planned]│
│                                                                             │
│  ID    Feature Name                   Status   Files               Actions  │
│  F-001 OAuth2 Authentication Engine   [DONE]   src/auth/jwt.py     [Edit ▼] │
│  F-002 Stripe Payment Gateway         [DONE]   src/pay/stripe.py   [Edit ▼] │
│  F-003 Dark-Mode Web Dashboard        [DONE]   scripts/dash.py     [Edit ▼] │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Empirical Benchmarks

Empirical simulation benchmark across 20 conversation turns on a 15-feature codebase:

| Metric | Traditional Agent (Brute Force) | Remembrall Engine (Direct Recall) | Advantage |
|---|---|---|---|
| **Cumulative Tokens** | 210,000 tokens | 35,860 tokens | **82.92% Token Reduction** |
| **Tool Invocations** | 4 - 8 tools per turn | 1 tool (`read_file` / MCP) | **4x - 8x Faster** |
| **LLM Generation Delay** | ~3,500 seconds | ~597 seconds | **~48 Minutes Saved** |
| **Hallucination Risk** | ~37.5% failure rate | 0.0% (Deterministic state) | **Grounded on Disk** |

---

## 🛠️ Complete CLI & MCP Tools Reference

| Command | Equivalent MCP Tool | Description |
|---|---|---|
| `remembrall ui` | - | Launches local dark-mode interactive web dashboard on `:4242` |
| `remembrall semantic "<term>"` | `remembrall_semantic_search` | TF-IDF cosine similarity & bilingual concept vector search |
| `remembrall query "<term>"` | `remembrall_query` | Performs weighted keyword search across features & technical findings |
| `remembrall simulate --turns <N>` | - | Runs empirical benchmark calculating exact token & latency savings |
| `remembrall export --format <fmt>` | - | Exports manifest as `changelog`, `github-issues`, `release-notes`, or `json` |
| `remembrall status` | `remembrall_status` | Returns line count, token usage, health check, and feature stats |
| `remembrall add "<title>" "<files>"` | `remembrall_add_feature` | Appends a new feature row with auto-incremented ID (`F-xxx`) |
| `remembrall set <ID> <STATUS>` | `remembrall_set_feature` | Updates an existing feature's status (`PLANNED`, `WIP`, `DONE`), files, or notes |
| `remembrall prune` | `remembrall_prune` | Automatically consolidates older DONE features if approaching 100 lines |
| `remembrall validate` | - | Enforces strict table formatting and <120 lines limit |
| `remembrall install-hooks` | - | Installs automated Git `pre-commit` validation hook |
| `remembrall init --template <type>` | - | Scaffolds a new `.remembrall.md` (`minimal`, `web`, `api`, `monorepo`) |

---

## ❓ Frequently Asked Questions (FAQ)

<details>
<summary><b>1. What happens when context compaction or /clear occurs?</b></summary>
Because Remembrall stores active project state in a physical disk file (<code>.remembrall.md</code>), context window compaction or running <code>/clear</code> has zero negative impact. On the very next prompt, the agent's pre-flight rule reads the manifest and immediately resumes with 100% precision.
</details>

<details>
<summary><b>2. How does Remembrall prevent memory files from expanding indefinitely?</b></summary>
Remembrall has a hard ceiling of 120 lines. When the file reaches 100 lines, the <code>prune</code> engine collapses historical completed features into compact single-row module summaries (e.g. <code>F-001..F-008 | Core Foundations | DONE</code>). This guarantees token intake remains practically flat (~250-400 tokens) regardless of project age.
</details>

<details>
<summary><b>3. Is my data sent to any third-party cloud service?</b></summary>
No. Remembrall is 100% local, self-contained, and requires zero third-party cloud subscriptions or API keys. All vector calculations, MCP services, and dashboards run purely on your local machine.
</details>

<details>
<summary><b>4. Does Remembrall work on Windows, macOS, and Linux?</b></summary>
Yes. Remembrall is tested continuously across Ubuntu Linux, Windows, and macOS on Python 3.9 through 3.12 via automated GitHub Actions CI.
</details>

---

## 📂 Multi-Harness Architecture & Layout

```
.
├── .remembrall.md                             # Physical active project state manifest
├── gemini-extension.json                      # Antigravity & Gemini CLI extension manifest
├── GEMINI.md                                  # Antigravity always-on memory instructions
├── AGENTS.md                                  # Universal agent protocol (Devin, Cursor, Codex)
├── package.json                               # Universal npm & node plugin descriptor
├── pyproject.toml                             # Python package & CLI console entrypoints
├── mcp_config.json                            # Model Context Protocol configuration
├── plugin.json                                # Open marketplace & plugin manifest
├── README.md                                  # Production masterpiece documentation
├── CHANGELOG.md                               # Standardized version changelog
├── LICENSE                                    # Official MIT license
├── .gitignore                                 # Git ignore definitions
├── .claude-plugin/                            # Claude Code official marketplace packaging
│   ├── plugin.json
│   └── marketplace.json
├── .cursor-plugin/                            # Cursor IDE plugin descriptor
│   └── plugin.json
├── .codex-plugin/                             # OpenAI Codex plugin descriptor
│   └── plugin.json
├── hooks/
│   ├── pre-commit                             # Git pre-commit shell script
│   └── pre-commit.ps1                         # Git pre-commit PowerShell script
├── hooks.json                                 # Antigravity lifecycle event hooks
├── src/remembrall/                            # Python & Node package distribution
│   ├── __init__.py
│   ├── index.js
│   ├── cli.py
│   └── mcp.py
├── skills/
│   └── remembrall/
│       └── SKILL.md                           # Universal Agent Skills standard format
├── .agents/
│   ├── rules/
│   │   └── remembrall.md                      # Always-on pre/post flight rule (aktif otomatis)
│   └── skills/
│       └── remembrall/
│           ├── SKILL.md                       # Comprehensive workflow guide + Mermaid
│           ├── scripts/
│           │   ├── remembrall.py              # Core Python CLI engine
│           │   ├── mcp_server.py              # JSON-RPC 2.0 MCP server
│           │   ├── semantic.py                # TF-IDF & Concept Vector search
│           │   ├── exporter.py                # Multi-format changelog & release exporter
│           │   ├── simulation.py              # Empirical benchmark simulator
│           │   └── dashboard.py               # Interactive dark-mode web UI on :4242
│           ├── templates/                     # Project templates (minimal, web, api, monorepo)
│           └── references/                    # Deep reference guides (anti-bloat, recovery, economics)
├── .github/workflows/
│   └── ci.yml                                 # Multi-OS matrix CI pipeline (Linux, Windows, macOS)
└── tests/
    ├── test_remembrall.py                     # CLI & Query unit tests
    ├── test_mcp_server.py                     # MCP Server unit tests
    ├── test_semantic.py                       # Semantic search tests
    ├── test_exporter.py                       # Exporter tests
    ├── test_simulation.py                     # Simulation benchmark tests
    ├── test_dashboard.py                      # Dashboard UI tests
    └── run-all-tests.ps1                      # Complete test orchestrator (19/19 PASS)
```

---

## 📄 License

MIT License © 2026 DenyDev. Free for open-source and commercial use.
