import fs from "node:fs";
import path from "node:path";
import http from "node:http";
import child_process from "node:child_process";

export const MAX_LINES = 120;
export const PRUNE_TRIGGER_LINES = 100;

export function findManifest(startDir = process.cwd()) {
  let curr = path.resolve(startDir);
  while (true) {
    const candidate = path.join(curr, ".remembrall.md");
    if (fs.existsSync(candidate)) return candidate;
    const parent = path.dirname(curr);
    if (parent === curr) break;
    curr = parent;
  }
  return path.join(process.cwd(), ".remembrall.md");
}

export function parseManifest(content) {
  const lines = content.split(/\r?\n/);
  const features = [];
  const findings = [];
  let section = "overview";

  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed.startsWith("## Feature Manifest")) {
      section = "features";
      continue;
    } else if (trimmed.startsWith("## Technical Findings")) {
      section = "findings";
      continue;
    } else if (trimmed.startsWith("## ")) {
      section = "other";
      continue;
    }

    if (section === "features" && trimmed.startsWith("|") && !trimmed.includes("| ID |") && !trimmed.includes("|---|")) {
      const parts = line.split("|").map(p => p.trim());
      if (parts.length >= 6) {
        features.push({
          id: parts[1],
          name: parts[2],
          status: parts[3],
          files: parts[4],
          note: parts[5]
        });
      }
    } else if (section === "findings" && (trimmed.startsWith("- **") || trimmed.startsWith("* **"))) {
      const match = line.match(/[-*]\s*\*\*([^*:]+):?\*\*:?\s*(.*)/);
      if (match) {
        findings.push({ title: match[1].trim(), content: match[2].trim() });
      }
    }
  }

  return { lines, features, findings };
}

export function validateManifest(manifestPath) {
  if (!fs.existsSync(manifestPath)) {
    return { valid: false, error: `File not found: ${manifestPath}` };
  }
  const content = fs.readFileSync(manifestPath, "utf-8");
  const { lines, features } = parseManifest(content);

  const errors = [];
  if (lines.length > MAX_LINES) {
    errors.push(`Manifest exceeds ${MAX_LINES} lines (currently ${lines.length}). Run 'prune'.`);
  }
  if (!content.includes("# Project Overview")) errors.push("Missing '# Project Overview' section.");
  if (!content.includes("## Feature Manifest")) errors.push("Missing '## Feature Manifest' section.");
  if (!content.includes("## Technical Findings")) errors.push("Missing '## Technical Findings' section.");

  for (const f of features) {
    if (!["DONE", "WIP", "PLANNED", "DEPRECATED"].includes(f.status)) {
      errors.push(`Feature ${f.id} has invalid status '${f.status}'.`);
    }
  }

  return {
    valid: errors.length === 0,
    lineCount: lines.length,
    featureCount: features.length,
    errors
  };
}

export function addFeature(manifestPath, id, name, files = "", note = "") {
  if (!fs.existsSync(manifestPath)) {
    throw new Error(`Manifest not found at ${manifestPath}`);
  }
  const content = fs.readFileSync(manifestPath, "utf-8");
  const lines = content.split(/\r?\n/);
  const newRow = `| ${id} | ${name} | PLANNED | ${files} | ${note} |`;

  let lastRowIdx = -1;
  let inTable = false;
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes("| ID |")) {
      inTable = true;
      continue;
    }
    if (inTable) {
      if (lines[i].trim().startsWith("|")) {
        lastRowIdx = i;
      } else if (lines[i].trim().startsWith("##") || lines[i].trim().startsWith("---")) {
        break;
      }
    }
  }

  const insertIdx = lastRowIdx !== -1 ? lastRowIdx + 1 : lines.length;

  lines.splice(insertIdx, 0, newRow);
  fs.writeFileSync(manifestPath, lines.join("\n"), "utf-8");
  return { success: true, id, lineCount: lines.length };
}

export function setFeature(manifestPath, id, status, note = null) {
  if (!fs.existsSync(manifestPath)) {
    throw new Error(`Manifest not found at ${manifestPath}`);
  }
  const content = fs.readFileSync(manifestPath, "utf-8");
  const lines = content.split(/\r?\n/);
  let updated = false;

  const newLines = lines.map(line => {
    if (line.trim().startsWith(`| ${id} `) || line.trim().startsWith(`| ${id}|`)) {
      const parts = line.split("|").map(p => p.trim());
      if (parts.length >= 6) {
        parts[3] = status;
        if (note !== null) parts[5] = note;
        updated = true;
        return `| ${parts[1]} | ${parts[2]} | ${parts[3]} | ${parts[4]} | ${parts[5]} |`;
      }
    }
    return line;
  });

  if (!updated) {
    throw new Error(`Feature ID '${id}' not found in manifest.`);
  }

  fs.writeFileSync(manifestPath, newLines.join("\n"), "utf-8");
  return { success: true, id, status };
}

export function queryMemory(manifestPath, queryStr, limit = 5) {
  if (!fs.existsSync(manifestPath)) return { features: [], findings: [] };
  const content = fs.readFileSync(manifestPath, "utf-8");
  const { features, findings } = parseManifest(content);
  const terms = queryStr.toLowerCase().split(/\s+/).filter(Boolean);

  function score(text) {
    const lower = text.toLowerCase();
    let s = 0;
    for (const t of terms) {
      if (lower.includes(t)) s += 10;
    }
    return s;
  }

  const scoredFeatures = features
    .map(f => ({ ...f, score: score(`${f.id} ${f.name} ${f.files} ${f.note}`) }))
    .filter(f => f.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, limit);

  const scoredFindings = findings
    .map(fd => ({ ...fd, score: score(`${fd.title} ${fd.content}`) }))
    .filter(fd => fd.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, limit);

  return { features: scoredFeatures, findings: scoredFindings };
}

export function pruneManifest(manifestPath) {
  if (!fs.existsSync(manifestPath)) throw new Error(`Manifest not found at ${manifestPath}`);
  const content = fs.readFileSync(manifestPath, "utf-8");
  const lines = content.split(/\r?\n/);

  if (lines.length < PRUNE_TRIGGER_LINES) {
    return { pruned: false, message: `Manifest has ${lines.length} lines. Below threshold (${PRUNE_TRIGGER_LINES}).` };
  }

  const { features } = parseManifest(content);
  const doneFeatures = features.filter(f => f.status === "DONE");
  if (doneFeatures.length <= 5) {
    return { pruned: false, message: "Not enough DONE features to consolidate." };
  }

  // Consolidate older half of DONE features
  const toConsolidate = doneFeatures.slice(0, Math.floor(doneFeatures.length / 2));
  const ids = toConsolidate.map(f => f.id);
  const summaryRow = `| ${ids[0]}-${ids[ids.length - 1]} | Consolidated Module (${ids.length} features) | DONE | multiple | Historical features archived in .remembrall.archive.md |`;

  // Preserve in L2 Cold Archive (.remembrall.archive.md) so zero details are ever lost
  const archivePath = path.join(path.dirname(manifestPath), ".remembrall.archive.md");
  let archiveHeader = "";
  if (!fs.existsSync(archivePath)) {
    archiveHeader = `# 🗄️ Remembrall Cold Storage Archive\nPermanent historical archive of consolidated features.\n\n| ID | Fitur | Status | File Terkait | Catatan | Archived At |\n|---|---|---|---|---|---|\n`;
  }
  const timestamp = new Date().toISOString().split("T")[0];
  const archiveRows = toConsolidate.map(f => `| ${f.id} | ${f.name} | ${f.status} | ${f.files} | ${f.note} | ${timestamp} |`).join("\n") + "\n";
  fs.appendFileSync(archivePath, archiveHeader + archiveRows, "utf-8");

  const newLines = [];
  let insertedSummary = false;

  for (const line of lines) {
    const trimmed = line.trim();
    const isTarget = ids.some(id => trimmed.startsWith(`| ${id} `) || trimmed.startsWith(`| ${id}|`));
    if (isTarget) {
      if (!insertedSummary) {
        newLines.push(summaryRow);
        insertedSummary = true;
      }
      continue;
    }
    newLines.push(line);
  }

  fs.writeFileSync(manifestPath, newLines.join("\n"), "utf-8");
  return { pruned: true, oldLines: lines.length, newLines: newLines.length, consolidated: ids.length };
}

export function generateHandoff(manifestPath) {
  if (!fs.existsSync(manifestPath)) return "No active manifest found.";
  const content = fs.readFileSync(manifestPath, "utf-8");
  const { lines, features, findings } = parseManifest(content);

  const done = features.filter(f => f.status === "DONE").length;
  const wip = features.filter(f => f.status === "WIP");
  const planned = features.filter(f => f.status === "PLANNED");

  return [
    `# 🔮 Remembrall Session Handoff`,
    `Generated at: ${new Date().toISOString()}`,
    ``,
    `## 📊 State Overview`,
    `- Total Features: ${features.length} (Done: ${done}, WIP: ${wip.length}, Planned: ${planned.length})`,
    `- Manifest Budget: ${lines.length}/${MAX_LINES} lines (~${Math.round(lines.length * 20)} tokens)`,
    ``,
    `## 🚧 In Progress (WIP)`,
    wip.length > 0 ? wip.map(w => `- [${w.id}] **${w.name}**: ${w.note} (${w.files})`).join("\n") : "_No active WIP tasks._",
    ``,
    `## 🎯 Next Up (PLANNED)`,
    planned.slice(0, 3).map(p => `- [${p.id}] **${p.name}**: ${p.files}`).join("\n"),
    ``,
    `## 💡 Key Architectural Invariants`,
    findings.map(f => `- **${f.title}**: ${f.content}`).join("\n")
  ].join("\n");
}

export function checkDrift(manifestPath) {
  if (!fs.existsSync(manifestPath)) return { inSync: false, message: "Manifest not found" };
  const content = fs.readFileSync(manifestPath, "utf-8");
  const { features } = parseManifest(content);

  const manifestFiles = new Set();
  for (const f of features) {
    f.files.split(",").forEach(fl => {
      const clean = fl.trim();
      if (clean) manifestFiles.add(path.normalize(clean));
    });
  }

  let gitFiles = [];
  try {
    const raw = child_process.execSync("git status --porcelain", { encoding: "utf-8" });
    gitFiles = raw
      .split(/\r?\n/)
      .filter(line => line.length > 3)
      .map(line => line.substring(3).trim())
      .filter(f => f && !f.startsWith(".git") && !f.startsWith(".remembrall") && !f.endsWith(".md"));
  } catch {
    return { inSync: true, message: "Not a git repo or git unavailable" };
  }

  const unrecorded = gitFiles.filter(gf => !manifestFiles.has(path.normalize(gf)));
  return {
    inSync: unrecorded.length === 0,
    unrecorded,
    gitFilesCount: gitFiles.length
  };
}

export function startDashboard(manifestPath, port = 4242) {
  const htmlFile = path.join(path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Z]:)/, "$1")), "dashboard.html");

  const server = http.createServer((req, res) => {
    if (req.url === "/api/status") {
      const content = fs.existsSync(manifestPath) ? fs.readFileSync(manifestPath, "utf-8") : "";
      const parsed = parseManifest(content);
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ manifest: manifestPath, ...parsed }));
      return;
    }

    const content = fs.existsSync(manifestPath) ? fs.readFileSync(manifestPath, "utf-8") : "";
    const { features } = parseManifest(content);
    const doneCount = features.filter(f => f.status === "DONE").length;

    let html = fs.existsSync(htmlFile) ? fs.readFileSync(htmlFile, "utf-8") : "<h1>Remembrall</h1>";
    html = html.replace('id="stat-total" class="text-2xl font-bold text-cyan-400">0</div>', `id="stat-total" class="text-2xl font-bold text-cyan-400">${features.length}</div>`);
    html = html.replace('id="stat-done" class="text-2xl font-bold text-emerald-400">0</div>', `id="stat-done" class="text-2xl font-bold text-emerald-400">${doneCount}</div>`);
    
    const rows = features.map(f => `
      <tr class="hover:bg-slate-800/30">
        <td class="p-4 font-mono font-bold text-cyan-400">${f.id}</td>
        <td class="p-4 font-medium">${f.name}</td>
        <td class="p-4"><span class="px-2.5 py-0.5 rounded-full text-xs font-semibold ${f.status === "DONE" ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : f.status === "WIP" ? "bg-amber-500/10 text-amber-400 border border-amber-500/20" : "bg-slate-800 text-slate-400"}">${f.status}</span></td>
        <td class="p-4 font-mono text-xs text-slate-400">${f.files}</td>
        <td class="p-4 text-xs text-slate-400">${f.note}</td>
      </tr>
    `).join("");

    html = html.replace('<tbody id="features-table" class="divide-y divide-slate-800/60">', `<tbody id="features-table" class="divide-y divide-slate-800/60">${rows}`);

    res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
    res.end(html);
  });

  server.listen(port, () => {
    console.log(`🔮 Remembrall Node Dashboard listening on http://localhost:${port}`);
  });

  return server;
}

export function captureGit(manifestPath, options = {}) {
  let commitMsg = "Git commit capture";
  let changedFiles = [];
  try {
    commitMsg = child_process.execSync("git log -1 --pretty=%s", { encoding: "utf-8" }).trim();
    const rawFiles = child_process.execSync("git diff-tree --no-commit-id --name-only -r HEAD", { encoding: "utf-8" });
    changedFiles = rawFiles.split(/\r?\n/).map(f => f.trim()).filter(Boolean);
  } catch {
    // fallback if no git history yet
  }

  const { features } = parseManifest(fs.readFileSync(manifestPath, "utf-8"));
  let nextId = options.id;
  if (!nextId) {
    let maxNum = 0;
    for (const f of features) {
      const m = f.id.match(/^F-(\d+)/);
      if (m) maxNum = Math.max(maxNum, parseInt(m[1], 10));
    }
    nextId = `F-${String(maxNum + 1).padStart(3, "0")}`;
  }

  const title = options.name || commitMsg || "Captured Git Feature";
  const files = options.files || changedFiles.slice(0, 3).join(", ") || "multiple";
  const status = options.status || "DONE";
  const note = options.note || `Auto-captured from git commit: ${commitMsg}`;

  addFeature(manifestPath, nextId, title, files, note);
  if (status !== "PLANNED") {
    setFeature(manifestPath, nextId, status, note);
  }

  return { id: nextId, title, files, status, note };
}

export function generateMermaidDiagram(manifestPath, format = "flowchart") {
  if (!fs.existsSync(manifestPath)) return "%% Manifest not found";
  const { features } = parseManifest(fs.readFileSync(manifestPath, "utf-8"));

  if (format === "gantt") {
    const lines = [
      "gantt",
      "    title Remembrall State Engine Roadmap",
      "    dateFormat YYYY-MM-DD",
      "    axisFormat %m/%d",
      "    section Completed Features"
    ];
    features.filter(f => f.status === "DONE").slice(-8).forEach((f, idx) => {
      lines.push(`    ${f.id} ${f.name.replace(/[:#]/g, "")} :done, f${idx}, 2026-11-17, 1d`);
    });
    const wip = features.filter(f => f.status === "WIP");
    if (wip.length > 0) {
      lines.push("    section In Progress");
      wip.forEach((f, idx) => {
        lines.push(`    ${f.id} ${f.name.replace(/[:#]/g, "")} :active, w${idx}, after f0, 2d`);
      });
    }
    return lines.join("\n");
  }

  // Default: Flowchart
  const lines = [
    "flowchart LR",
    "    classDef done fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#ecfdf5;",
    "    classDef wip fill:#78350f,stroke:#f59e0b,stroke-width:2px,color:#fffbeb;",
    "    classDef planned fill:#1e293b,stroke:#64748b,stroke-width:2px,color:#f8fafc;"
  ];

  // Group into last 10 features for readable diagram
  const recent = features.slice(-10);
  for (let i = 0; i < recent.length; i++) {
    const f = recent[i];
    const safeName = f.name.replace(/["\(\)\[\]]/g, "");
    const className = f.status.toLowerCase();
    lines.push(`    ${f.id.replace(/-/g, "_")}["${f.id}: ${safeName}"]:::${className}`);
    if (i > 0) {
      const prev = recent[i - 1];
      lines.push(`    ${prev.id.replace(/-/g, "_")} --> ${f.id.replace(/-/g, "_")}`);
    }
  }

  return lines.join("\n");
}

export function socraticAlign(manifestPath, featureId) {
  if (!fs.existsSync(manifestPath)) throw new Error("Manifest not found");
  const { features, findings } = parseManifest(fs.readFileSync(manifestPath, "utf-8"));
  const feature = features.find(f => f.id === featureId);
  if (!feature) throw new Error(`Feature ${featureId} not found in manifest.`);

  const invariantPrompts = findings.slice(0, 3).map((fd, i) => `${i + 1}. [${fd.title}]: Does your implementation strictly comply with: "${fd.content}"?`);

  return [
    `# 🧙‍♂️ Remembrall Socratic Pre-Flight Alignment (${feature.id})`,
    `Feature Target: **${feature.name}** [Status: ${feature.status}]`,
    `Files in Scope: \`${feature.files || "unspecified"}\``,
    ``,
    `## 🎯 Jane Street Diagnostic Alignment Questions:`,
    ...invariantPrompts,
    `${invariantPrompts.length + 1}. [Non-Goals]: What files or behaviors must explicitly NOT be touched?`,
    `${invariantPrompts.length + 2}. [Verification Evidence]: What exact test command proves completion before setting DONE?`,
    ``,
    `💡 Rule: Verify all answers in chat context before transitioning status from PLANNED to WIP.`
  ].join("\n");
}

export function generateBridge(manifestPath, targetAgent = "cursor") {
  if (!fs.existsSync(manifestPath)) return "No active manifest found.";
  const { lines, features, findings } = parseManifest(fs.readFileSync(manifestPath, "utf-8"));
  const done = features.filter(f => f.status === "DONE").length;
  const wip = features.filter(f => f.status === "WIP");

  const stateSummary = `Active Features: ${features.length} (${done} Done, ${wip.length} WIP). Line budget: ${lines.length}/120.`;

  switch (targetAgent.toLowerCase()) {
    case "cursor":
      return [
        `# .cursorrules - Remembrall State Invariant`,
        `# Always consult .remembrall.md before scanning workspace.`,
        `Project State: ${stateSummary}`,
        `Current WIP: ${wip.map(w => w.id + ": " + w.name).join(", ") || "None"}`,
        `Mandatory Gate: Always run 'node bin/remembrall.js sync' before finishing turn.`
      ].join("\n");

    case "claude":
      return [
        `<remembrall_memory version="1.0">`,
        `  <state budget="${lines.length}/120" completed="${done}" total="${features.length}"/>`,
        `  <wip_tasks>${wip.map(w => `${w.id}: ${w.name}`).join("; ") || "none"}</wip_tasks>`,
        `  <invariants>${findings.map(f => f.title).join(", ")}</invariants>`,
        `  <instruction>Read .remembrall.md directly. Do not re-scan codebase.</instruction>`,
        `</remembrall_memory>`
      ].join("\n");

    case "codex":
    case "antigravity":
    default:
      return [
        `# Universal Agent Context Brief (${targetAgent.toUpperCase()})`,
        `State: ${stateSummary}`,
        `Protocol: Inspect .remembrall.md at Turn 1. Update status before reporting DONE.`
      ].join("\n");
  }
}
