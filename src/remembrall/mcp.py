import sys
from pathlib import Path
import importlib.util

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
