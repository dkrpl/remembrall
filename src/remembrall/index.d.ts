/**
 * Remembrall: Universal Zero-Amnesia State Engine
 */

export interface Feature {
  id: string;
  name: string;
  status: "DONE" | "WIP" | "PLANNED" | "DEPRECATED";
  files: string;
  note: string;
  score?: number;
}

export interface Finding {
  title: string;
  content: string;
  score?: number;
}

export interface ManifestState {
  lines: string[];
  features: Feature[];
  findings: Finding[];
}

export interface ValidationResult {
  valid: boolean;
  lineCount: number;
  featureCount: number;
  errors: string[];
}

export function findManifest(startDir?: string): string;
export function parseManifest(content: string): ManifestState;
export function validateManifest(manifestPath: string): ValidationResult;
export function addFeature(manifestPath: string, id: string, name: string, files?: string, note?: string): { success: boolean; id: string; lineCount: number };
export function setFeature(manifestPath: string, id: string, status: string, note?: string | null): { success: boolean; id: string; status: string };
export function queryMemory(manifestPath: string, queryStr: string, limit?: number): { features: Feature[]; findings: Finding[] };
export function pruneManifest(manifestPath: string): { pruned: boolean; message?: string; oldLines?: number; newLines?: number; consolidated?: number };
export function generateHandoff(manifestPath: string): string;
export function startDashboard(manifestPath: string, port?: number): any;
