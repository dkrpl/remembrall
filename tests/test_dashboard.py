import unittest
import tempfile
import shutil
import sys
from pathlib import Path

# Add scripts directory
sys.path.insert(0, str(Path(__file__).parent.parent / ".agents" / "skills" / "remembrall" / "scripts"))
import dashboard
import remembrall

class TestDashboard(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.manifest_path = Path(self.test_dir) / ".remembrall.md"
        remembrall.init_manifest(self.manifest_path, template="minimal")
        remembrall.add_feature(self.manifest_path, "UI Navigation Bar", "src/nav.tsx", notes="Top nav", status="DONE")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_generate_html_contains_features(self):
        html = dashboard.generate_html(self.manifest_path)
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("Remembrall", html)
        self.assertIn("UI Navigation Bar", html)
        self.assertIn("F-002", html)

    def test_dashboard_api_payload(self):
        data = dashboard.get_api_data(self.manifest_path)
        self.assertEqual(data["stats"]["total_features"], 2)
        self.assertEqual(data["stats"]["done"], 2)
        self.assertEqual(len(data["features"]), 2)

if __name__ == "__main__":
    unittest.main()
