#!/usr/bin/env python3
"""
Remembrall CLI - Autonomous state & persistent feature tracker for AI coding agents.
Zero third-party dependencies. Compatible with Python 3.8+.
"""

import argparse
import os
import re
import sys
from pathlib import Path

# Ensure UTF-8 output across all operating systems and Windows console (cp1252)
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add scripts dir to path for internal imports
SCRIPT_DIR = Path(__file__).parent.resolve()
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import semantic
import exporter
import simulation
import dashboard

DEFAULT_MANIFEST_NAME = ".remembrall.md"
MAX_LINES_DEFAULT = 120
PRUNE_TRIGGER_DEFAULT = 100

TEMPLATE_MINIMAL = """# Project Overview
- **Project:** {project_name}
- **Core Stack:** {stack}
- **Purpose:** {purpose}

---

## Feature Manifest
| ID | Fitur | Status | File Terkait | Catatan |
|---|---|---|---|---|
| F-001 | Initial Setup | DONE | README.md | Project scaffolded |

---

## Technical Findings
- Core architectural constraints and invariant decisions (max 5 bullets).
"""

TEMPLATE_WEB = """# Project Overview
- **Project:** {project_name}
- **Core Stack:** TypeScript, Next.js / React, TailwindCSS, Node.js
- **Purpose:** Fullstack modern web application

---

## Feature Manifest
| ID | Fitur | Status | File Terkait | Catatan |
|---|---|---|---|---|
| F-001 | Project Scaffolding | DONE | package.json, src/ | Next.js and Tailwind setup |

---

## Technical Findings
- Client/Server separation: all API logic inside `src/app/api/` or server actions.
- State management: React context or Zustand; avoid unnecessary global stores.
"""

TEMPLATE_API = """# Project Overview
- **Project:** {project_name}
- **Core Stack:** Python, FastAPI / Flask, SQLite / PostgreSQL
- **Purpose:** High-performance RESTful API service

---

## Feature Manifest
| ID | Fitur | Status | File Terkait | Catatan |
|---|---|---|---|---|
| F-001 | API Core Engine | DONE | app/main.py, requirements.txt | Base router and environment config |

---

## Technical Findings
- All endpoints follow REST standards with Pydantic schema validation.
- Database sessions handled via dependency injection (`db/session.py`).
"""

TEMPLATES = {
    "minimal": TEMPLATE_MINIMAL,
    "web": TEMPLATE_WEB,
    "api": TEMPLATE_API
}

FEATURE_ROW_REGEX = re.compile(
    r"^\|\s*(F-\d+(?:\.\.F-\d+)?)\s*\|\s*([^\|]+)\s*\|\s*(DONE|WIP|PLANNED)\s*\|\s*([^\|]+)\s*\|\s*([^\|]*)\s*\|"
)


def find_manifest(start_path=None):
    current = Path(start_path or Path.cwd()).resolve()
    for directory in [current] + list(current.parents):
        target = directory / DEFAULT_MANIFEST_NAME
        if target.exists():
            return target
    return current / DEFAULT_MANIFEST_NAME


def init_manifest(path, template="minimal", project_name="My Project", stack="Polyglot", purpose="Built with agentic assistance"):
    tmpl = TEMPLATES.get(template, TEMPLATE_MINIMAL)
    rendered = tmpl.format(project_name=project_name, stack=stack, purpose=purpose)
    Path(path).write_text(rendered, encoding="utf-8")
    return path


def parse_features(path):
    path = Path(path)
    if not path.exists():
        return {}
    lines = path.read_text(encoding="utf-8").splitlines()
    features = {}
    for idx, line in enumerate(lines):
        m = FEATURE_ROW_REGEX.match(line.strip())
        if m:
            fid = m.group(1).strip()
            features[fid] = {
                "id": fid,
                "title": m.group(2).strip(),
                "status": m.group(3).strip(),
                "files": m.group(4).strip(),
                "notes": m.group(5).strip(),
                "line_idx": idx,
                "raw": line
            }
    return features


def get_next_id(features):
    max_num = 0
    for fid in features.keys():
        m = re.match(r"^F-(\d+)", fid)
        if m:
            num = int(m.group(1))
            if num > max_num:
                max_num = num
    return f"F-{max_num + 1:03d}"


def add_feature(path, title, files, notes="", status="PLANNED"):
    path = Path(path)
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()
    features = parse_features(path)
    new_id = get_next_id(features)
    
    new_row = f"| {new_id} | {title} | {status} | {files} | {notes} |"
    
    # Locate last feature row or table header
    table_insert_idx = -1
    for idx, line in enumerate(lines):
        if line.strip().startswith("|") and ("| ID |" in line or "|---|" in line or FEATURE_ROW_REGEX.match(line.strip())):
            table_insert_idx = idx
            
    if table_insert_idx != -1:
        lines.insert(table_insert_idx + 1, new_row)
    else:
        lines.append(new_row)
        
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return new_id


def set_feature(path, fid, status=None, files=None, notes=None):
    path = Path(path)
    lines = path.read_text(encoding="utf-8").splitlines()
    updated = False
    
    for idx, line in enumerate(lines):
        m = FEATURE_ROW_REGEX.match(line.strip())
        if m and m.group(1).strip() == fid:
            cur_title = m.group(2).strip()
            cur_status = status if status else m.group(3).strip()
            cur_files = files if files else m.group(4).strip()
            cur_notes = notes if notes is not None else m.group(5).strip()
            lines[idx] = f"| {fid} | {cur_title} | {cur_status} | {cur_files} | {cur_notes} |"
            updated = True
            break
            
    if not updated:
        raise ValueError(f"Feature ID {fid} not found in {path}")
        
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return fid


def prune_manifest(path, max_individual=8):
    """
    Consolidates older DONE features into a single summary row when table grows.
    """
    path = Path(path)
    lines = path.read_text(encoding="utf-8").splitlines()
    features = parse_features(path)
    
    done_features = [f for f in features.values() if f["status"] == "DONE" and ".." not in f["id"]]
    if len(done_features) <= max_individual:
        return 0
        
    to_consolidate = done_features[:-max_individual]
    if len(to_consolidate) < 2:
        return 0
        
    first_id = to_consolidate[0]["id"]
    last_id = to_consolidate[-1]["id"]
    range_id = f"{first_id}..{last_id}"
    
    # Collect files
    combined_files = []
    for f in to_consolidate:
        for p in f["files"].split(","):
            p_strip = p.strip()
            if p_strip and p_strip not in combined_files:
                combined_files.append(p_strip)
                
    files_summary = ", ".join(combined_files[:3])
    if len(combined_files) > 3:
        files_summary += f" (+{len(combined_files) - 3} more)"
        
    consolidated_row = f"| {range_id} | Consolidated Foundation Modules ({len(to_consolidate)} features) | DONE | {files_summary} | Stabilized historical features archived in .remembrall.archive.md |"
    
    # Preserve pruned features into L2 Cold Storage Archive (.remembrall.archive.md)
    archive_path = path.parent / ".remembrall.archive.md"
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    header = ""
    if not archive_path.exists():
        header = "# 🗄️ Remembrall Cold Storage Archive\nPermanent historical archive of consolidated features.\n\n| ID | Fitur | Status | File Terkait | Catatan | Archived At |\n|---|---|---|---|---|---|\n"
    rows = "\n".join([f"| {f['id']} | {f['title']} | {f['status']} | {f['files']} | {f['notes']} | {today} |" for f in to_consolidate]) + "\n"
    with open(archive_path, "a", encoding="utf-8") as af:
        af.write(header + rows)
    
    # Filter out consolidated lines
    indices_to_remove = set(f["line_idx"] for f in to_consolidate)
    first_idx = to_consolidate[0]["line_idx"]
    
    new_lines = []
    for idx, line in enumerate(lines):
        if idx in indices_to_remove:
            if idx == first_idx:
                new_lines.append(consolidated_row)
            continue
        new_lines.append(line)
        
    path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return len(to_consolidate)


def query_memory(path, query_str, limit=5):
    """
    Search features and technical findings with weighted term matching.
    """
    path = Path(path)
    if not path.exists():
        return {"query": query_str, "features": [], "findings": []}
        
    content = path.read_text(encoding="utf-8")
    features = parse_features(path)
    
    # Extract findings
    findings = []
    in_findings = False
    for line in content.splitlines():
        if "## Technical Findings" in line:
            in_findings = True
            continue
        elif in_findings and line.startswith("#"):
            in_findings = False
        elif in_findings:
            stripped = line.strip()
            if stripped.startswith("-") or stripped.startswith("*"):
                findings.append(stripped.lstrip("-* ").strip())
                
    query_terms = [t.lower() for t in re.findall(r"\w+", query_str)]
    if not query_terms:
        return {"query": query_str, "features": [], "findings": []}
        
    scored_features = []
    clean_query = query_str.lower().strip()
    
    for fid, f in features.items():
        score = 0
        title_lower = f["title"].lower()
        files_lower = f["files"].lower()
        notes_lower = f["notes"].lower()
        combined = f"{title_lower} {files_lower} {notes_lower}"
        
        # Exact phrase bonus
        if clean_query in combined:
            score += 15
            
        for term in query_terms:
            if term in title_lower:
                score += 10
            if term in files_lower:
                score += 6
            if term in notes_lower:
                score += 4
                
        if score > 0:
            scored_features.append({
                "id": fid,
                "title": f["title"],
                "status": f["status"],
                "files": f["files"],
                "notes": f["notes"],
                "score": score
            })
            
    scored_features.sort(key=lambda x: x["score"], reverse=True)
    
    scored_findings = []
    for bullet in findings:
        b_lower = bullet.lower()
        b_score = 0
        if clean_query in b_lower:
            b_score += 15
        for term in query_terms:
            if term in b_lower:
                b_score += 8
        if b_score > 0:
            scored_findings.append({"text": bullet, "score": b_score})
            
    scored_findings.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "query": query_str,
        "features": scored_features[:limit],
        "findings": scored_findings[:limit]
    }


def semantic_search(path, query_str, limit=5):
    """
    Search features using TF-IDF cosine vector similarity and concept synonyms.
    """
    features = parse_features(path)
    feature_list = list(features.values())
    engine = semantic.SemanticEngine(feature_list)
    results = engine.search(query_str, limit=limit)
    return {
        "query": query_str,
        "results": results
    }


def get_stats(path):
    path = Path(path)
    if not path.exists():
        return {"exists": False, "total_features": 0, "is_valid": False}
        
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()
    line_count = len(lines)
    features = parse_features(path)
    
    done = sum(1 for f in features.values() if f["status"] == "DONE")
    wip = sum(1 for f in features.values() if f["status"] == "WIP")
    planned = sum(1 for f in features.values() if f["status"] == "PLANNED")
    
    char_count = len(content)
    est_tokens = char_count // 4
    
    is_valid = (
        "# Project Overview" in content and
        "## Feature Manifest" in content and
        "## Technical Findings" in content and
        line_count <= MAX_LINES_DEFAULT
    )
    
    return {
        "exists": True,
        "path": str(path),
        "lines": line_count,
        "char_count": char_count,
        "est_tokens": est_tokens,
        "total_features": len(features),
        "done": done,
        "wip": wip,
        "planned": planned,
        "is_valid": is_valid,
        "needs_pruning": line_count >= PRUNE_TRIGGER_DEFAULT
    }


def install_hooks(repo_dir=None):
    """
    Installs pre-commit hook into .git/hooks/
    """
    repo_path = Path(repo_dir or Path.cwd()).resolve()
    git_hooks_dir = repo_path / ".git" / "hooks"
    if not (repo_path / ".git").exists():
        return {"success": False, "message": f"No .git directory found at {repo_path}"}
        
    git_hooks_dir.mkdir(parents=True, exist_ok=True)
    target_hook = git_hooks_dir / "pre-commit"
    
    source_hook = Path(__file__).parent.parent.parent.parent.parent / "hooks" / "pre-commit"
    if not source_hook.exists():
        # Fallback to local
        source_hook = repo_path / "hooks" / "pre-commit"
        
    if not source_hook.exists():
        return {"success": False, "message": "Source hook template hooks/pre-commit not found"}
        
    content = source_hook.read_text(encoding="utf-8")
    target_hook.write_text(content, encoding="utf-8")
    try:
        os.chmod(target_hook, 0o755)
    except Exception:
        pass
        
    return {"success": True, "path": str(target_hook)}


def generate_handoff(path):
    """
    Generates a token-optimized session transition brief for subagents or new sessions.
    """
    stats = get_stats(path)
    features = parse_features(path)
    content = Path(path).read_text(encoding="utf-8") if Path(path).exists() else ""
    
    # Extract findings
    findings = []
    in_findings = False
    for line in content.splitlines():
        if "## Technical Findings" in line:
            in_findings = True
        elif in_findings and line.startswith("#"):
            in_findings = False
        elif in_findings and (line.strip().startswith("-") or line.strip().startswith("*")):
            findings.append(line.strip().lstrip("-* ").strip())

    wip_features = [f for f in features.values() if f["status"] == "WIP"]
    planned_features = [f for f in features.values() if f["status"] == "PLANNED"]
    
    lines = [
        "=== REMEMBRALL SESSION HANDOFF BRIEF ===",
        f"Manifest: {stats.get('path', str(path))}",
        f"Active Metrics: {stats.get('total_features', 0)} Features Total [DONE: {stats.get('done', 0)} | WIP: {stats.get('wip', 0)} | PLANNED: {stats.get('planned', 0)}]",
    ]
    
    if wip_features:
        lines.append("\n⚡ CURRENT ACTIVE WORK (WIP):")
        for f in wip_features:
            lines.append(f"- [{f['id']}] {f['title']} (Files: {f['files']})")
            if f["notes"]:
                lines.append(f"  Notes: {f['notes']}")
    else:
        lines.append("\n⚡ CURRENT ACTIVE WORK: No WIP features currently open.")

    if planned_features:
        lines.append("\n📋 NEXT UP (PLANNED):")
        for f in planned_features[:3]:
            lines.append(f"- [{f['id']}] {f['title']}")

    if findings:
        lines.append("\n🔒 CORE INVARIANTS & CONSTRAINTS:")
        for b in findings[:4]:
            lines.append(f"- {b}")

    lines.append("\n👉 NEXT AGENT ACTION: Read primary files for current task directly; do not run recursive scans.")
    lines.append("========================================")
    
    return "\n".join(lines) + "\n"


def setup_wizard(target_dir=None):
    """
    Interactive/auto-detecting onboarding wizard for new repositories.
    """
    base_path = Path(target_dir or Path.cwd()).resolve()
    manifest_target = base_path / DEFAULT_MANIFEST_NAME
    
    # Auto-detect stack
    template = "minimal"
    project_name = base_path.name
    
    if (base_path / "package.json").exists() or (base_path / "next.config.js").exists():
        template = "web"
    elif (base_path / "pyproject.toml").exists() or (base_path / "requirements.txt").exists():
        template = "api"
        
    if not manifest_target.exists():
        init_manifest(manifest_target, template=template, project_name=project_name)
        scaffolded = True
    else:
        scaffolded = False
        
    hook_res = install_hooks(repo_dir=base_path)
    
    return {
        "manifest_path": str(manifest_target),
        "scaffolded": scaffolded,
        "template_used": template,
        "hooks_installed": hook_res["success"],
        "hook_path": hook_res.get("path")
    }


def main():
    parser = argparse.ArgumentParser(description="Remembrall - Autonomous State & Feature Memory Engine")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # status
    p_status = subparsers.add_parser("status", help="Display manifest status & token metrics")
    p_status.add_argument("--file", help="Path to .remembrall.md")
    
    # init
    p_init = subparsers.add_parser("init", help="Scaffold a new .remembrall.md")
    p_init.add_argument("--file", default=DEFAULT_MANIFEST_NAME, help="Destination path")
    p_init.add_argument("--template", choices=["minimal", "web", "api"], default="minimal", help="Template type")
    p_init.add_argument("--name", default="Project", help="Project name")
    
    # add
    p_add = subparsers.add_parser("add", help="Add a new feature to the manifest")
    p_add.add_argument("title", help="Feature name/title")
    p_add.add_argument("files", help="Associated files (comma-separated)")
    p_add.add_argument("--notes", default="", help="Brief note")
    p_add.add_argument("--status", choices=["PLANNED", "WIP", "DONE"], default="PLANNED", help="Initial status")
    p_add.add_argument("--file", help="Path to .remembrall.md")
    
    # set
    p_set = subparsers.add_parser("set", help="Update feature status or notes")
    p_set.add_argument("id", help="Feature ID (e.g. F-002)")
    p_set.add_argument("status", choices=["PLANNED", "WIP", "DONE"], help="New status")
    p_set.add_argument("--files", help="Update files")
    p_set.add_argument("--notes", help="Update notes")
    p_set.add_argument("--file", help="Path to .remembrall.md")
    
    # prune
    p_prune = subparsers.add_parser("prune", help="Consolidate older DONE features to save tokens")
    p_prune.add_argument("--threshold", type=int, default=8, help="Maximum individual features to keep")
    p_prune.add_argument("--file", help="Path to .remembrall.md")
    
    # validate
    p_val = subparsers.add_parser("validate", help="Validate manifest structure and budget limits")
    p_val.add_argument("--file", help="Path to .remembrall.md")

    # query
    p_query = subparsers.add_parser("query", help="Search memory for features and architectural findings")
    p_query.add_argument("search", help="Search keywords or phrase")
    p_query.add_argument("--limit", type=int, default=5, help="Maximum results to return")
    p_query.add_argument("--file", help="Path to .remembrall.md")

    # semantic
    p_sem = subparsers.add_parser("semantic", help="Search memory using AI concept & vector similarity")
    p_sem.add_argument("search", help="Concept query (e.g. 'masuk akun', 'bayar langganan')")
    p_sem.add_argument("--limit", type=int, default=5, help="Maximum results")
    p_sem.add_argument("--file", help="Path to .remembrall.md")

    # install-hooks
    p_hooks = subparsers.add_parser("install-hooks", help="Install git pre-commit hook into current repository")
    p_hooks.add_argument("--repo", help="Path to repository root (defaults to CWD)")

    # setup
    p_setup = subparsers.add_parser("setup", help="Auto-detect project stack, initialize manifest, and install hooks")
    p_setup.add_argument("--dir", help="Project directory path (defaults to CWD)")

    # handoff
    p_hand = subparsers.add_parser("handoff", help="Generate a token-optimized session transition brief for subagents or new sessions")
    p_hand.add_argument("--file", help="Path to .remembrall.md")

    # export
    p_exp = subparsers.add_parser("export", help="Export manifest as changelog, github-issues, release-notes, or json")
    p_exp.add_argument("--format", choices=["changelog", "github-issues", "release-notes", "json"], default="changelog", help="Output format")
    p_exp.add_argument("--version", default="1.0.0", help="Version tag for changelog/release notes")
    p_exp.add_argument("--out", help="Optional output destination file path")
    p_exp.add_argument("--file", help="Path to .remembrall.md")

    # simulate
    p_sim = subparsers.add_parser("simulate", help="Run benchmark comparing Amnesic agent scanning vs Remembrall targeted recall")
    p_sim.add_argument("--turns", type=int, default=15, help="Number of simulated session turns (default 15)")
    p_sim.add_argument("--file", help="Path to .remembrall.md")

    # ui
    p_ui = subparsers.add_parser("ui", help="Launch the local interactive dark-mode web dashboard")
    p_ui.add_argument("--port", type=int, default=4242, help="Port to listen on (default 4242)")
    p_ui.add_argument("--no-browser", action="store_true", help="Do not automatically open browser")
    p_ui.add_argument("--file", help="Path to .remembrall.md")
    
    args = parser.parse_args()
    target_file = Path(args.file) if getattr(args, "file", None) else find_manifest()
    
    if args.command == "init":
        out = init_manifest(target_file, template=args.template, project_name=args.name)
        print(f"Initialized {out} with template '{args.template}'")
        sys.exit(0)
        
    if not target_file.exists():
        print(f"Error: Manifest {target_file} not found. Run 'remembrall init' first.", file=sys.stderr)
        sys.exit(1)
        
    if args.command == "status":
        stats = get_stats(target_file)
        print(f"\n🔮 Remembrall State Engine ({stats['path']})")
        print(f"   Lines: {stats['lines']} / {MAX_LINES_DEFAULT} (Tokens ~{stats['est_tokens']})")
        print(f"   Features Total: {stats['total_features']} [DONE: {stats['done']} | WIP: {stats['wip']} | PLANNED: {stats['planned']}]")
        print(f"   Health Check: {'PASS' if stats['is_valid'] else 'FAIL'}")
        if stats["needs_pruning"]:
            print("   ⚠️  File is approaching 100 lines. Recommended to run: remembrall prune")
        print()
        
    elif args.command == "add":
        new_id = add_feature(target_file, args.title, args.files, notes=args.notes, status=args.status)
        print(f"Added [{new_id}] {args.title} ({args.status}) -> {target_file}")
        
    elif args.command == "set":
        set_feature(target_file, args.id, status=args.status, files=args.files, notes=args.notes)
        print(f"Updated [{args.id}] to {args.status} -> {target_file}")
        
    elif args.command == "prune":
        count = prune_manifest(target_file, max_individual=args.threshold)
        print(f"Pruned & consolidated {count} historical features.")
        
    elif args.command == "validate":
        stats = get_stats(target_file)
        if not stats["is_valid"]:
            print(f"FAIL: {target_file} violated structural constraints or line limits.", file=sys.stderr)
            sys.exit(1)
        print(f"PASS: {target_file} is healthy and token-optimized.")
        sys.exit(0)

    elif args.command == "query":
        results = query_memory(target_file, args.search, limit=args.limit)
        print(f"\n🔍 Remembrall Query: '{results['query']}'")
        if results["features"]:
            print("   Features Matching:")
            for f in results["features"]:
                print(f"   - [{f['id']}] {f['title']} ({f['status']}) [Score: {f['score']}]")
                print(f"     Files: {f['files']}")
                if f["notes"]:
                    print(f"     Notes: {f['notes']}")
        else:
            print("   No features matched.")

        if results["findings"]:
            print("\n   Technical Findings Matching:")
            for b in results["findings"]:
                print(f"   - {b['text']} [Score: {b['score']}]")
        print()

    elif args.command == "semantic":
        res = semantic_search(target_file, args.search, limit=args.limit)
        print(f"\n🧠 Remembrall Semantic Vector Search: '{res['query']}'")
        if res["results"]:
            for item in res["results"]:
                pct = int(item["similarity"] * 100)
                print(f"   - [{item['id']}] {item['title']} ({item['status']}) [Relevance: {pct}%]")
                print(f"     Files: {item['files']}")
                if item["notes"]:
                    print(f"     Notes: {item['notes']}")
        else:
            print("   No semantic matches found.")
        print()

    elif args.command == "install-hooks":
        res = install_hooks(repo_dir=args.repo)
        if res["success"]:
            print(f"✅ Git pre-commit hook installed successfully at: {res['path']}")
        else:
            print(f"⚠️ {res['message']}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "setup":
        res = setup_wizard(target_dir=args.dir)
        print(f"\n🔮 Remembrall Setup Complete:")
        print(f"   Manifest: {res['manifest_path']} ({'Newly scaffolded' if res['scaffolded'] else 'Existing retained'})")
        print(f"   Template: {res['template_used']}")
        if res["hooks_installed"]:
            print(f"   Git Pre-commit Hook: Installed ({res['hook_path']})")
        print("   Status: Zero-amnesia tracking active.\n")

    elif args.command == "handoff":
        brief = generate_handoff(target_file)
        print(brief)

    elif args.command == "export":
        if args.format == "changelog":
            out_str = exporter.export_changelog(target_file, version=args.version)
        elif args.format == "github-issues":
            out_str = exporter.export_github_issues(target_file)
        elif args.format == "release-notes":
            out_str = exporter.export_release_notes(target_file, tag=f"v{args.version}")
        elif args.format == "json":
            out_str = exporter.export_json(target_file)

        if args.out:
            Path(args.out).write_text(out_str, encoding="utf-8")
            print(f"Exported {args.format} to: {args.out}")
        else:
            print(out_str)

    elif args.command == "simulate":
        b = simulation.run_benchmark(target_file, simulated_turns=args.turns)
        print(f"\n⚡ Remembrall Zero-Amnesia Benchmark ({b['simulated_turns']} Turns Simulated)")
        print(f"   Features Tracked: {b['features_tracked']} (Manifest Cost: ~{b['manifest_token_size']} tokens)")
        print(f"   Amnesic Agent (Brute Force Scan): {b['total_amnesic_tokens']:,} tokens (Accuracy ~{b['amnesic_accuracy']}%)")
        print(f"   Remembrall Agent (Direct Recall): {b['total_remembrall_tokens']:,} tokens (Accuracy {b['remembrall_accuracy']}%)")
        print(f"   ------------------------------------------------------------")
        print(f"   🎯 Tokens Saved: {b['tokens_saved']:,} tokens ({b['token_savings_pct']}% Reduction)")
        print(f"   ⏱️  Time Saved: ~{b['estimated_seconds_saved']} seconds of LLM generation delay\n")

    elif args.command == "ui":
        dashboard.start_server(target_file, port=args.port, open_browser=not args.no_browser)


if __name__ == "__main__":
    main()
