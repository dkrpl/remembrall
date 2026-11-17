import unittest
import sys
from pathlib import Path

# Add scripts directory
sys.path.insert(0, str(Path(__file__).parent.parent / ".agents" / "skills" / "remembrall" / "scripts"))
import semantic

class TestSemanticSearch(unittest.TestCase):
    def setUp(self):
        self.corpus = [
            {
                "id": "F-001",
                "title": "OAuth2 Authentication Engine",
                "files": "src/auth/jwt.py",
                "notes": "Bearer token verification and Google login",
                "status": "DONE"
            },
            {
                "id": "F-002",
                "title": "Stripe Payment Gateway",
                "files": "src/billing/checkout.ts",
                "notes": "Handles customer subscriptions and invoices",
                "status": "DONE"
            },
            {
                "id": "F-003",
                "title": "Database Schema Migrations",
                "files": "src/db/alembic.py",
                "notes": "PostgreSQL connection pool setup",
                "status": "DONE"
            }
        ]
        self.engine = semantic.SemanticEngine(self.corpus)

    def test_semantic_synonym_matching(self):
        # Query "signin user" should find F-001 (OAuth2 Authentication) via concept mapping
        results = self.engine.search("signin user")
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["id"], "F-001")
        self.assertGreater(results[0]["similarity"], 0.3)

    def test_semantic_payment_matching(self):
        # Query "bayar langganan" should match F-002 (Stripe Payment Gateway)
        results = self.engine.search("bayar langganan")
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["id"], "F-002")

    def test_cosine_similarity_ranking(self):
        # Exact keyword match
        results = self.engine.search("postgresql alembic database")
        self.assertEqual(results[0]["id"], "F-003")

if __name__ == "__main__":
    unittest.main()
