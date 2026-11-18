import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import {
  parseManifest,
  validateManifest,
  addFeature,
  setFeature,
  queryMemory,
  pruneManifest,
  generateHandoff,
  generateMermaidDiagram,
  socraticAlign,
  generateBridge,
  captureGit
} from "../src/remembrall/engine.js";

const SAMPLE_MANIFEST = `# Project Overview
- **Project:** Test App
- **Purpose:** Testing Remembrall Engine

---

## Feature Manifest
| ID | Fitur | Status | File Terkait | Catatan |
|---|---|---|---|---|
| F-001 | Auth | DONE | src/auth.js | JWT login |
| F-002 | Billing | WIP | src/bill.js | Stripe integration |

---

## Technical Findings
- **Zero Re-scan:** Active memory test.
`;

test("parseManifest parses features and findings accurately", () => {
  const parsed = parseManifest(SAMPLE_MANIFEST);
  assert.equal(parsed.features.length, 2);
  assert.equal(parsed.features[0].id, "F-001");
  assert.equal(parsed.features[0].status, "DONE");
  assert.equal(parsed.features[1].id, "F-002");
  assert.equal(parsed.features[1].status, "WIP");
  assert.equal(parsed.findings.length, 1);
  assert.equal(parsed.findings[0].title, "Zero Re-scan");
});

test("validateManifest validates line budget and structure", () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "remembrall-test-"));
  const tmpFile = path.join(tmpDir, ".remembrall.md");
  fs.writeFileSync(tmpFile, SAMPLE_MANIFEST, "utf-8");

  const res = validateManifest(tmpFile);
  assert.equal(res.valid, true);
  assert.equal(res.featureCount, 2);

  fs.rmSync(tmpDir, { recursive: true, force: true });
});

test("addFeature appends a new row in PLANNED status", () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "remembrall-test-"));
  const tmpFile = path.join(tmpDir, ".remembrall.md");
  fs.writeFileSync(tmpFile, SAMPLE_MANIFEST, "utf-8");

  addFeature(tmpFile, "F-003", "Dashboard", "src/dash.js", "Analytics UI");
  const parsed = parseManifest(fs.readFileSync(tmpFile, "utf-8"));
  assert.equal(parsed.features.length, 3);
  assert.equal(parsed.features[2].id, "F-003");
  assert.equal(parsed.features[2].status, "PLANNED");

  fs.rmSync(tmpDir, { recursive: true, force: true });
});

test("setFeature updates status and note", () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "remembrall-test-"));
  const tmpFile = path.join(tmpDir, ".remembrall.md");
  fs.writeFileSync(tmpFile, SAMPLE_MANIFEST, "utf-8");

  setFeature(tmpFile, "F-002", "DONE", "Stripe completed");
  const parsed = parseManifest(fs.readFileSync(tmpFile, "utf-8"));
  assert.equal(parsed.features[1].status, "DONE");
  assert.equal(parsed.features[1].note, "Stripe completed");

  fs.rmSync(tmpDir, { recursive: true, force: true });
});

test("queryMemory searches keywords correctly", () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "remembrall-test-"));
  const tmpFile = path.join(tmpDir, ".remembrall.md");
  fs.writeFileSync(tmpFile, SAMPLE_MANIFEST, "utf-8");

  const res = queryMemory(tmpFile, "JWT");
  assert.equal(res.features.length, 1);
  assert.equal(res.features[0].id, "F-001");

  fs.rmSync(tmpDir, { recursive: true, force: true });
});

test("generateHandoff creates markdown brief", () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "remembrall-test-"));
  const tmpFile = path.join(tmpDir, ".remembrall.md");
  fs.writeFileSync(tmpFile, SAMPLE_MANIFEST, "utf-8");

  const handoff = generateHandoff(tmpFile);
  assert.match(handoff, /Remembrall Session Handoff/);
  assert.match(handoff, /In Progress \(WIP\)/);

  fs.rmSync(tmpDir, { recursive: true, force: true });
});

test("pruneManifest creates L2 cold storage archive preserving history", () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "remembrall-test-"));
  const tmpFile = path.join(tmpDir, ".remembrall.md");

  let rows = "";
  for (let i = 3; i <= 20; i++) {
    rows += `| F-${String(i).padStart(3, "0")} | Feature ${i} | DONE | file${i}.js | Done note |\n`;
  }
  let bigManifest = SAMPLE_MANIFEST.replace("| F-002 | Billing | WIP | src/bill.js | Stripe integration |\n", `| F-002 | Billing | WIP | src/bill.js | Stripe integration |\n${rows}`);
  for (let j = 0; j < 85; j++) {
    bigManifest += `<!-- padding ${j} -->\n`;
  }
  fs.writeFileSync(tmpFile, bigManifest, "utf-8");

  const res = pruneManifest(tmpFile);
  assert.equal(res.pruned, true);

  const archiveFile = path.join(tmpDir, ".remembrall.archive.md");
  assert.equal(fs.existsSync(archiveFile), true);
  const archiveContent = fs.readFileSync(archiveFile, "utf-8");
  assert.match(archiveContent, /Remembrall Cold Storage Archive/);
  assert.match(archiveContent, /F-001/);

  fs.rmSync(tmpDir, { recursive: true, force: true });
});

test("generateMermaidDiagram generates flowchart and gantt diagrams", () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "remembrall-test-"));
  const tmpFile = path.join(tmpDir, ".remembrall.md");
  fs.writeFileSync(tmpFile, SAMPLE_MANIFEST, "utf-8");

  const flowchart = generateMermaidDiagram(tmpFile, "flowchart");
  assert.match(flowchart, /flowchart LR/);
  assert.match(flowchart, /F_001/);

  const gantt = generateMermaidDiagram(tmpFile, "gantt");
  assert.match(gantt, /gantt/);

  fs.rmSync(tmpDir, { recursive: true, force: true });
});

test("socraticAlign produces diagnostic invariant questions", () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "remembrall-test-"));
  const tmpFile = path.join(tmpDir, ".remembrall.md");
  fs.writeFileSync(tmpFile, SAMPLE_MANIFEST, "utf-8");

  const res = socraticAlign(tmpFile, "F-001");
  assert.match(res, /Jane Street Diagnostic Alignment/);
  assert.match(res, /Zero Re-scan/);
  assert.match(res, /Non-Goals/);

  fs.rmSync(tmpDir, { recursive: true, force: true });
});

test("generateBridge exports agent-specific configurations", () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "remembrall-test-"));
  const tmpFile = path.join(tmpDir, ".remembrall.md");
  fs.writeFileSync(tmpFile, SAMPLE_MANIFEST, "utf-8");

  const cursor = generateBridge(tmpFile, "cursor");
  assert.match(cursor, /.cursorrules/);

  const claude = generateBridge(tmpFile, "claude");
  assert.match(claude, /<remembrall_memory/);

  fs.rmSync(tmpDir, { recursive: true, force: true });
});

test("captureGit captures git commit metadata into manifest", () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "remembrall-test-"));
  const tmpFile = path.join(tmpDir, ".remembrall.md");
  fs.writeFileSync(tmpFile, SAMPLE_MANIFEST, "utf-8");

  const res = captureGit(tmpFile, { id: "F-099", name: "OAuth Auth", status: "DONE", files: "src/oauth.js" });
  assert.equal(res.id, "F-099");
  assert.equal(res.status, "DONE");

  const parsed = parseManifest(fs.readFileSync(tmpFile, "utf-8"));
  assert.equal(parsed.features.some(f => f.id === "F-099"), true);

  fs.rmSync(tmpDir, { recursive: true, force: true });
});
