import sys
from pathlib import Path
import importlib.util

# Ensure UTF-8 output across all operating systems and Windows console (cp1252)
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def main():
    try:
        from remembrall import mcp
        if mcp and hasattr(mcp, "main"):
            mcp.main()
            return
    except Exception:
        pass

    script_path = Path(__file__).resolve().parent.parent.parent / ".agents" / "skills" / "remembrall" / "scripts" / "mcp_server.py"
    if script_path.exists():
        spec = importlib.util.spec_from_file_location("remembrall_mcp_cli", script_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.main()
    else:
        print("❌ Error: Could not locate Remembrall MCP server script.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
