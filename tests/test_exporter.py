import unittest
import tempfile
import shutil
import sys
from pathlib import Path

# Add scripts directory
sys.path.insert(0, str(Path(__file__).parent.parent / ".agents" / "skills" / "remembrall" / "scripts"))
import exporter
import remembrall

class TestExporter(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.manifest_path = Path(self.test_dir) / ".remembrall.md"
        remembrall.init_manifest(self.manifest_path, template="minimal")
        remembrall.add_feature(self.manifest_path, "OAuth2 Authentication", "src/auth.py", notes="Google Login", status="DONE")
        remembrall.add_feature(self.manifest_path, "Stripe Payments", "src/pay.py", notes="Stripe checkout", status="PLANNED")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_export_changelog(self):
        cl = exporter.export_changelog(self.manifest_path, version="1.0.0")
        self.assertIn("# Changelog", cl)
        self.assertIn("OAuth2 Authentication", cl)
        self.assertIn("### Added", cl)

    def test_export_github_issues(self):
        issues = exporter.export_github_issues(self.manifest_path)
        self.assertIn("gh issue create", issues)
        self.assertIn("Stripe Payments", issues)

    def test_export_release_notes(self):
        rn = exporter.export_release_notes(self.manifest_path, tag="v1.0.0")
        self.assertIn("Release v1.0.0", rn)
        self.assertIn("OAuth2 Authentication", rn)

if __name__ == "__main__":
    unittest.main()
