import fs from "node:fs";
import path from "node:path";
import http from "node:http";

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
  const summaryRow = `| ${ids[0]}-${ids[ids.length - 1]} | Consolidated Module (${ids.length} features) | DONE | multiple | Historical features archived |`;

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

export function startDashboard(manifestPath, port = 4242) {
  const server = http.createServer((req, res) => {
    if (req.url === "/api/status") {
      const content = fs.existsSync(manifestPath) ? fs.readFileSync(manifestPath, "utf-8") : "";
      const parsed = parseManifest(content);
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ manifest: manifestPath, ...parsed }));
      return;
    }

    const content = fs.existsSync(manifestPath) ? fs.readFileSync(manifestPath, "utf-8") : "";
    const { features, findings } = parseManifest(content);
    const doneCount = features.filter(f => f.status === "DONE").length;

    const html = `<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8"><title>Remembrall Dashboard (Node)</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen p-8 font-sans">
  <div class="max-w-6xl mx-auto space-y-6">
    <div class="flex items-center justify-between border-b border-slate-800 pb-4">
      <div>
        <h1 class="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-indigo-400">🔮 Remembrall State Engine</h1>
        <p class="text-xs text-slate-400 mt-1">Universal Zero-Amnesia Memory (Node.js Native)</p>
      </div>
      <div class="flex gap-4">
        <div class="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-center">
          <div class="text-2xl font-bold text-cyan-400">${features.length}</div>
          <div class="text-[10px] text-slate-400 uppercase tracking-wider">Features</div>
        </div>
        <div class="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-center">
          <div class="text-2xl font-bold text-emerald-400">${doneCount}</div>
          <div class="text-[10px] text-slate-400 uppercase tracking-wider">Completed</div>
        </div>
      </div>
    </div>
    <div class="bg-slate-900/60 rounded-2xl border border-slate-800 overflow-hidden">
      <table class="w-full text-left text-sm">
        <thead class="bg-slate-950/60 text-slate-400 border-b border-slate-800 uppercase text-xs">
          <tr><th class="p-4">ID</th><th class="p-4">Feature</th><th class="p-4">Status</th><th class="p-4">Files</th><th class="p-4">Notes</th></tr>
        </thead>
        <tbody class="divide-y divide-slate-800/60">
          ${features.map(f => `
            <tr class="hover:bg-slate-800/30">
              <td class="p-4 font-mono font-bold text-cyan-400">${f.id}</td>
              <td class="p-4 font-medium">${f.name}</td>
              <td class="p-4"><span class="px-2.5 py-0.5 rounded-full text-xs font-semibold ${f.status === "DONE" ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : f.status === "WIP" ? "bg-amber-500/10 text-amber-400 border border-amber-500/20" : "bg-slate-800 text-slate-400"}">${f.status}</span></td>
              <td class="p-4 font-mono text-xs text-slate-400">${f.files}</td>
              <td class="p-4 text-xs text-slate-400">${f.note}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>
  </div>
</body>
</html>`;

    res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
    res.end(html);
  });

  server.listen(port, () => {
    console.log(`🔮 Remembrall Node Dashboard listening on http://localhost:${port}`);
  });

  return server;
}
