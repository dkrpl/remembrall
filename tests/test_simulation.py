import unittest
import sys
from pathlib import Path

# Add scripts directory
sys.path.insert(0, str(Path(__file__).parent.parent / ".agents" / "skills" / "remembrall" / "scripts"))
import simulation

class TestSimulation(unittest.TestCase):
    def test_run_benchmark(self):
        manifest_path = Path(__file__).parent.parent / ".remembrall.md"
        bench = simulation.run_benchmark(manifest_path, simulated_turns=15)
        self.assertIn("token_savings_pct", bench)
        self.assertGreater(bench["token_savings_pct"], 75.0)
        self.assertGreater(bench["tokens_saved"], 10000)
        self.assertEqual(bench["remembrall_accuracy"], 100.0)

if __name__ == "__main__":
    unittest.main()
