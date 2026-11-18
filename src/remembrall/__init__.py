"""
Remembrall - World-Class Persistent Memory & Zero-Rescan State Engine for AI Coding Agents.
"""

__version__ = "1.0.0"

from pathlib import Path
import sys
import importlib.util

SCRIPT_DIR = Path(__file__).resolve().parent.parent.parent / ".agents" / "skills" / "remembrall" / "scripts"

def _load_module(name, filename):
    path = SCRIPT_DIR / filename
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

core = _load_module("remembrall_core", "remembrall.py")
mcp = _load_module("remembrall_mcp", "mcp_server.py")
