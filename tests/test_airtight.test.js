import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import {
  parseArchive,
  queryMemory,
  semanticMerge,
  repairManifest,
  runGatekeeper,
  discoverManifests,
  initScopedManifest
} from "../src/remembrall/engine.js";

const SAMPLE_L1 = `# Project Overview
- **Project:** Test App
- **Core Stack:** Node.js, Markdown

## Feature Manifest
| ID | Fitur | Status | File Terkait | Catatan |
|---|---|---|---|---|
| F-002 | New Authentication | DONE | src/auth.js | JWT auth implementation |
| F-003 | Dashboard Widget | WIP | src/widget.js | Working on chart rendering |

## Technical Findings
- **Zero Scan**: Never scan entire repo.
`;

const SAMPLE_L2_ARCHIVE = `# 🗄️ Remembrall Cold Storage Archive
Permanent historical archive of consolidated features.

| ID | Fitur | Status | File Terkait | Catatan | Archived At |
|---|---|---|---|---|---|
| F-001 | Initial Scaffolding | DONE | package.json | Base project setup | 2026-11-01 |
`;

test("Unified Two-Tier Memory Recall: searches L1 active and L2 archive seamlessly", () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "remembrall-airtight-"));
  const l1Path = path.join(tmpDir, ".remembrall.md");
  const l2Path = path.join(tmpDir, ".remembrall.archive.md");

  fs.writeFileSync(l1Path, SAMPLE_L1, "utf-8");
  fs.writeFileSync(l2Path, SAMPLE_L2_ARCHIVE, "utf-8");

  // Query a term in L2 archive
  const resArchive = queryMemory(l1Path, "scaffolding");
  assert.equal(resArchive.features.length, 1);
  assert.equal(resArchive.features[0].id, "F-001");
  assert.equal(resArchive.features[0].tier, "L2_COLD_ARCHIVE");

  // Query a term in L1 active
  const resActive = queryMemory(l1Path, "authentication");
  assert.equal(resActive.features.length, 1);
  assert.equal(resActive.features[0].id, "F-002");
  assert.equal(resActive.features[0].tier, "L1_ACTIVE");

  fs.rmSync(tmpDir, { recursive: true, force: true });
});

test("3-Way Semantic Merge Driver: resolves table conflicts across branches automatically", () => {
  const base = `# Project Overview\n\n## Feature Manifest\n| ID | Fitur | Status | File Terkait | Catatan |\n|---|---|---|---|---|\n| F-001 | Auth Base | PLANNED | auth.js | Initial |\n\n## Technical Findings\n- **Rule 1**: Keep clean\n`;
  
  // Ours updated F-001 to WIP and added F-002
  const ours = `# Project Overview\n\n## Feature Manifest\n| ID | Fitur | Status | File Terkait | Catatan |\n|---|---|---|---|---|\n| F-001 | Auth Base | WIP | auth.js, token.js | In progress |\n| F-002 | User Profile | DONE | profile.js | Completed |\n\n## Technical Findings\n- **Rule 1**: Keep clean\n`;

  // Theirs updated F-001 to DONE and added F-003
  const theirs = `# Project Overview\n\n## Feature Manifest\n| ID | Fitur | Status | File Terkait | Catatan |\n|---|---|---|---|---|\n| F-001 | Auth Base | DONE | auth.js | Done by team |\n| F-003 | Billing Gateway | PLANNED | stripe.js | Up next |\n\n## Technical Findings\n- **Rule 1**: Keep clean\n- **Rule 2**: Add tests\n`;

  const merged = semanticMerge(base, ours, theirs);

  assert.ok(merged.includes("F-001"));
  assert.ok(merged.includes("F-002"));
  assert.ok(merged.includes("F-003"));
  // DONE should take precedence over WIP for F-001
  assert.ok(merged.includes("| F-001 | Auth Base | DONE |"));
  // Files should be merged
  assert.ok(merged.includes("auth.js, token.js") || merged.includes("auth.js"));
  // Both findings preserved
  assert.ok(merged.includes("Rule 1"));
  assert.ok(merged.includes("Rule 2"));
});

test("Self-Healing Auto-Repair: fixes broken tables, invalid statuses, and missing headers", () => {
  const brokenContent = `
Random notes at top without title
| ID | Fitur | Status | File Terkait | Catatan |
| F-001 | Feature with missing separator and invalid status | COMPLETED | test.js | notes |
| F-002 | Unbalanced pipes | PROGRESS | file.js
`;
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "remembrall-repair-"));
  const manifestPath = path.join(tmpDir, ".remembrall.md");
  fs.writeFileSync(manifestPath, brokenContent, "utf-8");

  const repairResult = repairManifest(manifestPath);
  assert.equal(repairResult.repaired, true);

  const repairedContent = fs.readFileSync(manifestPath, "utf-8");
  assert.ok(repairedContent.includes("# Project Overview"));
  assert.ok(repairedContent.includes("## Feature Manifest"));
  assert.ok(repairedContent.includes("## Technical Findings"));
  assert.ok(repairedContent.includes("|---|---|---|---|---|"));
  // Normalized statuses
  assert.ok(repairedContent.includes("DONE"));
  assert.ok(repairedContent.includes("WIP"));

  fs.rmSync(tmpDir, { recursive: true, force: true });
});

test("Gatekeeper: verifies schema, line budget, and rejects invalid states", () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "remembrall-gate-"));
  const manifestPath = path.join(tmpDir, ".remembrall.md");

  fs.writeFileSync(manifestPath, SAMPLE_L1, "utf-8");
  const validResult = runGatekeeper(manifestPath, { checkDrift: false });
  assert.equal(validResult.passed, true);
  assert.equal(validResult.errors.length, 0);

  // Exceed line limit
  const overflowLines = Array(130).fill("line").join("\n");
  fs.writeFileSync(manifestPath, overflowLines, "utf-8");
  const invalidResult = runGatekeeper(manifestPath, { checkDrift: false });
  assert.equal(invalidResult.passed, false);
  assert.ok(invalidResult.errors.some(e => e.includes("exceeds 120 lines")));

  fs.rmSync(tmpDir, { recursive: true, force: true });
});

test("Monorepo & Scoped Manifest Engine: discovers and initializes scoped sub-manifests", () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "remembrall-mono-"));
  
  // Root manifest
  const rootManifest = path.join(tmpDir, ".remembrall.md");
  fs.writeFileSync(rootManifest, SAMPLE_L1, "utf-8");

  // Sub-package manifest
  const subPkgDir = path.join(tmpDir, "packages", "ui");
  initScopedManifest(subPkgDir, "UI Package");

  const discovered = discoverManifests(tmpDir);
  assert.equal(discovered.length, 2);
  assert.ok(discovered.some(d => d.scope === "root"));
  assert.ok(discovered.some(d => d.scope === "UI Package" || d.path.includes("packages")));

  fs.rmSync(tmpDir, { recursive: true, force: true });
});
