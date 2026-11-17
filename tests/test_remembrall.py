import unittest
import tempfile
import os
import shutil
import sys
from pathlib import Path

# Add scripts directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / ".agents" / "skills" / "remembrall" / "scripts"))
import remembrall

class TestRemembrallCLI(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.manifest_path = Path(self.test_dir) / ".remembrall.md"

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init_creates_valid_manifest(self):
        remembrall.init_manifest(self.manifest_path, template="minimal")
        self.assertTrue(self.manifest_path.exists())
        content = self.manifest_path.read_text(encoding="utf-8")
        self.assertIn("# Project Overview", content)
        self.assertIn("## Feature Manifest", content)
        self.assertIn("## Technical Findings", content)

    def test_add_and_set_feature(self):
        remembrall.init_manifest(self.manifest_path, template="minimal")
        new_id = remembrall.add_feature(self.manifest_path, "Authentication", "src/auth.py", notes="Initial auth", status="WIP")
        self.assertEqual(new_id, "F-002")
        
        # Verify it was added
        features = remembrall.parse_features(self.manifest_path)
        self.assertIn("F-002", features)
        self.assertEqual(features["F-002"]["status"], "WIP")

        # Set to DONE
        remembrall.set_feature(self.manifest_path, "F-002", status="DONE", notes="Auth finalized")
        features_after = remembrall.parse_features(self.manifest_path)
        self.assertEqual(features_after["F-002"]["status"], "DONE")
        self.assertEqual(features_after["F-002"]["notes"], "Auth finalized")

    def test_stats_and_validation(self):
        remembrall.init_manifest(self.manifest_path, template="minimal")
        stats = remembrall.get_stats(self.manifest_path)
        self.assertEqual(stats["total_features"], 1)
        self.assertEqual(stats["done"], 1)
        self.assertTrue(stats["is_valid"])

    def test_pruning_threshold(self):
        remembrall.init_manifest(self.manifest_path, template="minimal")
        # Add 10 features
        for i in range(10):
            remembrall.add_feature(self.manifest_path, f"Feature {i}", f"src/f{i}.py", status="DONE")
        
        features_before = remembrall.parse_features(self.manifest_path)
        self.assertEqual(len(features_before), 11)

        # Trigger prune
        pruned_count = remembrall.prune_manifest(self.manifest_path, max_individual=5)
        self.assertGreater(pruned_count, 0)
        
        content = self.manifest_path.read_text(encoding="utf-8")
        self.assertIn("Consolidated", content)

    def test_query_memory_ranking(self):
        remembrall.init_manifest(self.manifest_path, template="minimal")
        remembrall.add_feature(self.manifest_path, "OAuth2 Authentication", "src/auth/oauth.py", notes="Google and GitHub login", status="DONE")
        remembrall.add_feature(self.manifest_path, "Stripe Payments", "src/billing/stripe.py", notes="Checkout sessions", status="DONE")
        remembrall.add_feature(self.manifest_path, "User Profile Page", "src/pages/profile.tsx", notes="Display user avatar", status="WIP")

        # Query for 'auth'
        results = remembrall.query_memory(self.manifest_path, "auth")
        self.assertGreater(len(results["features"]), 0)
        self.assertEqual(results["features"][0]["id"], "F-002")

        # Query for 'stripe checkout'
        results_stripe = remembrall.query_memory(self.manifest_path, "stripe checkout")
        self.assertEqual(results_stripe["features"][0]["id"], "F-003")

        # Query for non-existent
        results_none = remembrall.query_memory(self.manifest_path, "nonexistenttermxyz")
        self.assertEqual(len(results_none["features"]), 0)

    def test_install_hooks_in_git_repo(self):
        # Fake a git repo in temp dir
        git_dir = Path(self.test_dir) / ".git"
        git_dir.mkdir()
        hooks_src = Path(self.test_dir) / "hooks"
        hooks_src.mkdir()
        (hooks_src / "pre-commit").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")

        res = remembrall.install_hooks(repo_dir=self.test_dir)
        self.assertTrue(res["success"])
        installed_hook = git_dir / "hooks" / "pre-commit"
        self.assertTrue(installed_hook.exists())

    def test_generate_handoff(self):
        remembrall.init_manifest(self.manifest_path, template="minimal")
        remembrall.add_feature(self.manifest_path, "Payment Processing", "src/pay.py", notes="Stripe integration", status="WIP")
        brief = remembrall.generate_handoff(self.manifest_path)
        self.assertIn("REMEMBRALL SESSION HANDOFF BRIEF", brief)
        self.assertIn("Payment Processing", brief)
        self.assertIn("WIP", brief)

if __name__ == "__main__":
    unittest.main()
