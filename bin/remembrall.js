#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import {
  findManifest,
  validateManifest,
  parseManifest,
  addFeature,
  setFeature,
  queryMemory,
  pruneManifest,
  generateHandoff,
  startDashboard
} from "../src/remembrall/engine.js";

const args = process.argv.slice(2);
const command = args[0] || "status";

function getManifestPath() {
  const customIdx = args.indexOf("--manifest");
  if (customIdx !== -1 && args[customIdx + 1]) {
    return path.resolve(args[customIdx + 1]);
  }
  return findManifest();
}

function printUsage() {
  console.log(`
🔮 Remembrall CLI (Universal Node Engine)
Usage:
  remembrall status                    Show active project status and progress
  remembrall validate                  Validate manifest syntax and line budget
  remembrall add --id <ID> --name <N>  Add a new feature row
  remembrall set <ID> <STATUS>         Update feature status (DONE, WIP, PLANNED)
  remembrall query <TERMS>             Fast token-weighted search
  remembrall prune                     Consolidate older features if over budget
  remembrall handoff                   Generate markdown handoff brief for AI
  remembrall ui [--port 4242]          Launch local dark-mode web dashboard
  remembrall install-hooks             Install Git pre-commit verification hook
  `);
}

async function main() {
  const manifestPath = getManifestPath();

  switch (command) {
    case "status": {
      if (!fs.existsSync(manifestPath)) {
        console.error(`❌ Manifest not found at: ${manifestPath}`);
        process.exit(1);
      }
      const content = fs.readFileSync(manifestPath, "utf-8");
      const { lines, features, findings } = parseManifest(content);
      const done = features.filter(f => f.status === "DONE").length;
      const wip = features.filter(f => f.status === "WIP").length;
      const planned = features.filter(f => f.status === "PLANNED").length;

      console.log(`\n🔮 Remembrall State Engine [Node v${process.version}]`);
      console.log(`   Manifest: ${manifestPath} (${lines.length}/120 lines, ~${lines.length * 20} tokens)`);
      console.log(`   Progress: ${done}/${features.length} Done (${Math.round((done / (features.length || 1)) * 100)}%) | ${wip} WIP | ${planned} Planned`);
      console.log("\nRecent Features:");
      for (const f of features.slice(-5)) {
        const icon = f.status === "DONE" ? "✅" : f.status === "WIP" ? "🚧" : "⏳";
        console.log(`   ${icon} [${f.id}] ${f.name.padEnd(30)} ${f.status.padEnd(8)} ${f.note}`);
      }
      break;
    }

    case "validate": {
      const res = validateManifest(manifestPath);
      if (res.valid) {
        console.log(`✅ PASS: ${manifestPath} is healthy (${res.lineCount} lines, ${res.featureCount} features).`);
      } else {
        console.error(`❌ FAIL: ${manifestPath} has errors:`);
        res.errors.forEach(e => console.error(`   - ${e}`));
        process.exit(1);
      }
      break;
    }

    case "add": {
      const idIdx = args.indexOf("--id");
      const nameIdx = args.indexOf("--name");
      const fileIdx = args.indexOf("--file");
      const noteIdx = args.indexOf("--note");

      const id = idIdx !== -1 ? args[idIdx + 1] : null;
      const name = nameIdx !== -1 ? args[nameIdx + 1] : null;
      const file = fileIdx !== -1 ? args[fileIdx + 1] : "";
      const note = noteIdx !== -1 ? args[noteIdx + 1] : "";

      if (!id || !name) {
        console.error("❌ Error: Both --id and --name are required.");
        process.exit(1);
      }

      addFeature(manifestPath, id, name, file, note);
      console.log(`✅ Added feature: ${id} - ${name}`);
      break;
    }

    case "set": {
      const id = args[1];
      const status = args[2]?.toUpperCase();
      const noteIdx = args.indexOf("--note");
      const note = noteIdx !== -1 ? args[noteIdx + 1] : null;

      if (!id || !status) {
        console.error("❌ Usage: remembrall set <ID> <STATUS> [--note '...']");
        process.exit(1);
      }

      setFeature(manifestPath, id, status, note);
      console.log(`✅ Updated feature ${id} status to ${status}.`);
      break;
    }

    case "query": {
      const queryStr = args.slice(1).filter(a => !a.startsWith("--")).join(" ");
      if (!queryStr) {
        console.error("❌ Usage: remembrall query <search terms>");
        process.exit(1);
      }
      const limitIdx = args.indexOf("--limit");
      const limit = limitIdx !== -1 ? parseInt(args[limitIdx + 1], 10) : 5;
      const results = queryMemory(manifestPath, queryStr, limit);

      console.log(`\n🔍 Memory search results for: "${queryStr}"`);
      if (results.features.length === 0) {
        console.log("   (No matching features found)");
      } else {
        results.features.forEach(f => {
          console.log(`   [${f.id}] (${f.status}) ${f.name} -> ${f.files} (Score: ${f.score})`);
        });
      }
      break;
    }

    case "prune": {
      const res = pruneManifest(manifestPath);
      if (res.pruned) {
        console.log(`✅ Pruned manifest: ${res.oldLines} lines -> ${res.newLines} lines (${res.consolidated} features consolidated).`);
      } else {
        console.log(`ℹ️ ${res.message}`);
      }
      break;
    }

    case "handoff": {
      const doc = generateHandoff(manifestPath);
      console.log(doc);
      break;
    }

    case "ui": {
      const portIdx = args.indexOf("--port");
      const port = portIdx !== -1 ? parseInt(args[portIdx + 1], 10) : 4242;
      startDashboard(manifestPath, port);
      break;
    }

    case "install-hooks": {
      const gitDir = path.join(process.cwd(), ".git");
      if (!fs.existsSync(gitDir)) {
        console.error("❌ Not a git repository.");
        process.exit(1);
      }
      const hooksDir = path.join(gitDir, "hooks");
      if (!fs.existsSync(hooksDir)) fs.mkdirSync(hooksDir, { recursive: true });
      const targetHook = path.join(hooksDir, "pre-commit");
      const sourceHook = path.join(process.cwd(), "hooks", "pre-commit");

      if (fs.existsSync(sourceHook)) {
        fs.copyFileSync(sourceHook, targetHook);
        try { fs.chmodSync(targetHook, 0o755); } catch {}
        console.log(`✅ Git pre-commit hook installed to: ${targetHook}`);
      } else {
        console.error("❌ Source hooks/pre-commit not found.");
        process.exit(1);
      }
      break;
    }

    case "help":
    case "--help":
    case "-h":
      printUsage();
      break;

    default:
      console.error(`Unknown command: '${command}'`);
      printUsage();
      process.exit(1);
  }
}

main().catch(err => {
  console.error("❌ Error:", err.message);
  process.exit(1);
});
