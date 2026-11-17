import unittest
import json
import tempfile
import shutil
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / ".agents" / "skills" / "remembrall" / "scripts"))
import mcp_server
import remembrall

class TestRemembrallMCPServer(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.manifest_path = Path(self.test_dir) / ".remembrall.md"
        remembrall.init_manifest(self.manifest_path, template="minimal")
        self.server = mcp_server.RemembrallMCPServer(manifest_path=self.manifest_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_initialize(self):
        req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"clientInfo": {"name": "test-client", "version": "1.0"}}
        }
        res = self.server.handle_request(req)
        self.assertEqual(res["id"], 1)
        self.assertIn("capabilities", res["result"])
        self.assertEqual(res["result"]["serverInfo"]["name"], "remembrall")

    def test_tools_list(self):
        req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        res = self.server.handle_request(req)
        tools = res["result"]["tools"]
        tool_names = [t["name"] for t in tools]
        self.assertIn("remembrall_status", tool_names)
        self.assertIn("remembrall_query", tool_names)
        self.assertIn("remembrall_add_feature", tool_names)
        self.assertIn("remembrall_set_feature", tool_names)
        self.assertIn("remembrall_prune", tool_names)

    def test_tool_call_status(self):
        req = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "remembrall_status",
                "arguments": {}
            }
        }
        res = self.server.handle_request(req)
        content = res["result"]["content"][0]["text"]
        self.assertIn("Remembrall State Engine", content)
        self.assertIn("Features Total", content)

    def test_tool_call_add_and_query(self):
        add_req = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "remembrall_add_feature",
                "arguments": {
                    "title": "Stripe Billing",
                    "files": "src/billing.py",
                    "notes": "Webhook handlers",
                    "status": "DONE"
                }
            }
        }
        add_res = self.server.handle_request(add_req)
        self.assertIn("F-002", add_res["result"]["content"][0]["text"])

        # Query tool
        query_req = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "remembrall_query",
                "arguments": {"query": "stripe"}
            }
        }
        query_res = self.server.handle_request(query_req)
        self.assertIn("Stripe Billing", query_res["result"]["content"][0]["text"])

        # Semantic tool
        sem_req = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "remembrall_semantic_search",
                "arguments": {"query": "payment customer"}
            }
        }
        sem_res = self.server.handle_request(sem_req)
        self.assertIn("Stripe Billing", sem_res["result"]["content"][0]["text"])

if __name__ == "__main__":
    unittest.main()
