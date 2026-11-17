"""
Remembrall - World-Class Persistent Memory & Zero-Rescan State Engine for AI Coding Agents.
"""

__version__ = "1.0.0"

from pathlib import Path
import sys

# Ensure internal scripts are discoverable
SCRIPT_DIR = Path(__file__).parent.parent.parent / ".agents" / "skills" / "remembrall" / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import remembrall as core
import mcp_server as mcp
