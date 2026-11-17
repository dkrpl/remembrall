#!/usr/bin/env python3
"""
Remembrall Model Context Protocol (MCP) Server.
Standard JSON-RPC 2.0 over stdio transport.
Enables AI agents (Antigravity, Cursor, Claude Code, Windsurf) to call Remembrall tools directly.
"""

import json
import os
import sys
from pathlib import Path

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent.resolve()
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import remembrall

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "remembrall"
SERVER_VERSION = "1.0.0"

TOOLS_DEFINITIONS = [
    {
        "name": "remembrall_status",
        "description": "Inspect active project memory manifest, line counts, token usage, and feature counts.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "manifest_path": {
                    "type": "string",
                    "description": "Optional custom path to .remembrall.md"
                }
            }
        }
    },
    {
        "name": "remembrall_query",
        "description": "Search active project memory for features, files, notes, and architectural findings by keyword.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keyword or phrase (e.g. 'auth', 'stripe checkout')"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default 5)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "remembrall_semantic_search",
        "description": "Search active memory using TF-IDF cosine similarity and concept synonyms (e.g. 'masuk akun' -> 'OAuth2 JWT').",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language or conceptual query"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum results (default 5)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "remembrall_add_feature",
        "description": "Register a new feature into the persistent memory manifest.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Title or name of the feature"},
                "files": {"type": "string", "description": "Comma-separated key file paths"},
                "notes": {"type": "string", "description": "Concise 1-line summary note"},
                "status": {
                    "type": "string",
                    "enum": ["PLANNED", "WIP", "DONE"],
                    "description": "Status of the feature (default PLANNED)"
                }
            },
            "required": ["title", "files"]
        }
    },
    {
        "name": "remembrall_set_feature",
        "description": "Update an existing feature status, touched files, or notes by feature ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Feature ID (e.g. F-001)"},
                "status": {"type": "string", "enum": ["PLANNED", "WIP", "DONE"]},
                "files": {"type": "string", "description": "Updated file paths"},
                "notes": {"type": "string", "description": "Updated 1-line note"}
            },
            "required": ["id"]
        }
    },
    {
        "name": "remembrall_prune",
        "description": "Automatically consolidate historical completed features to keep token count low (<120 lines).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "threshold": {
                    "type": "integer",
                    "description": "Number of individual recent features to retain before collapsing (default 8)"
                }
            }
        }
    }
]


class RemembrallMCPServer:
    def __init__(self, manifest_path=None):
        self.default_manifest_path = Path(manifest_path) if manifest_path else remembrall.find_manifest()

    def get_path(self, custom_path=None):
        if custom_path:
            return Path(custom_path)
        return self.default_manifest_path

    def handle_request(self, request):
        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": SERVER_NAME,
                        "version": SERVER_VERSION
                    }
                }
            }

        elif method == "notifications/initialized":
            return None

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": TOOLS_DEFINITIONS}
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            args = params.get("arguments", {})
            return self.execute_tool(req_id, tool_name, args)

        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found"
                }
            }

    def execute_tool(self, req_id, tool_name, args):
        manifest_path = self.get_path(args.get("manifest_path"))

        try:
            if tool_name == "remembrall_status":
                stats = remembrall.get_stats(manifest_path)
                text = (
                    f"🔮 Remembrall State Engine ({stats['path']})\n"
                    f"Lines: {stats['lines']} / {remembrall.MAX_LINES_DEFAULT} (Tokens ~{stats['est_tokens']})\n"
                    f"Features Total: {stats['total_features']} [DONE: {stats['done']} | WIP: {stats['wip']} | PLANNED: {stats['planned']}]\n"
                    f"Health Check: {'PASS' if stats['is_valid'] else 'FAIL'}\n"
                )
                if stats.get("needs_pruning"):
                    text += "⚠️ Warning: Manifest exceeds 100 lines. Pruning recommended.\n"
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": text}]}
                }

            elif tool_name == "remembrall_query":
                query_str = args.get("query", "")
                limit = args.get("limit", 5)
                res = remembrall.query_memory(manifest_path, query_str, limit=limit)
                lines = [f"🔍 Remembrall Query: '{query_str}'"]
                if res["features"]:
                    lines.append("Features Matched:")
                    for f in res["features"]:
                        lines.append(f"- [{f['id']}] {f['title']} ({f['status']}) [Score: {f['score']}]")
                        lines.append(f"  Files: {f['files']}")
                        if f["notes"]:
                            lines.append(f"  Notes: {f['notes']}")
                else:
                    lines.append("No features matched.")

                if res["findings"]:
                    lines.append("\nTechnical Findings Matched:")
                    for b in res["findings"]:
                        lines.append(f"- {b['text']} [Score: {b['score']}]")

                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": "\n".join(lines)}]}
                }

            elif tool_name == "remembrall_semantic_search":
                query_str = args.get("query", "")
                limit = args.get("limit", 5)
                res = remembrall.semantic_search(manifest_path, query_str, limit=limit)
                lines = [f"🧠 Remembrall Semantic Vector Search: '{query_str}'"]
                if res["results"]:
                    for item in res["results"]:
                        pct = int(item["similarity"] * 100)
                        lines.append(f"- [{item['id']}] {item['title']} ({item['status']}) [Relevance: {pct}%]")
                        lines.append(f"  Files: {item['files']}")
                        if item["notes"]:
                            lines.append(f"  Notes: {item['notes']}")
                else:
                    lines.append("No semantic matches found.")

                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": "\n".join(lines)}]}
                }

            elif tool_name == "remembrall_add_feature":
                title = args.get("title")
                files = args.get("files")
                notes = args.get("notes", "")
                status = args.get("status", "PLANNED")
                fid = remembrall.add_feature(manifest_path, title, files, notes=notes, status=status)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": f"Successfully registered [{fid}] {title} ({status}) in {manifest_path}"
                        }]
                    }
                }

            elif tool_name == "remembrall_set_feature":
                fid = args.get("id")
                status = args.get("status")
                files = args.get("files")
                notes = args.get("notes")
                remembrall.set_feature(manifest_path, fid, status=status, files=files, notes=notes)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": f"Successfully updated [{fid}] in {manifest_path}"
                        }]
                    }
                }

            elif tool_name == "remembrall_prune":
                threshold = args.get("threshold", 8)
                pruned = remembrall.prune_manifest(manifest_path, max_individual=threshold)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": f"Pruned & consolidated {pruned} historical features in {manifest_path}"
                        }]
                    }
                }

            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32602,
                        "message": f"Unknown tool: '{tool_name}'"
                    }
                }

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32000,
                    "message": str(e)
                }
            }

    def run_stdio(self):
        """Runs the JSON-RPC server loop over stdin/stdout."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                request = json.loads(line)
                response = self.handle_request(request)
                if response is not None:
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
            except Exception as e:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {e}"}
                }
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()


def main():
    server = RemembrallMCPServer()
    server.run_stdio()


if __name__ == "__main__":
    main()
