import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reviews" / "goal1631_v1_6_x_optix_extended_defer_collect_k_sweep_3ai_consensus_2026-05-09.md"
CLAUDE = ROOT / "docs" / "reviews" / "claude_goal1631_v1_6_x_optix_extended_defer_collect_k_sweep_review_2026-05-09.md"
GEMINI = ROOT / "docs" / "reviews" / "gemini_goal1631_v1_6_x_optix_extended_defer_collect_k_sweep_review_2026-05-09.md"


class Goal1631OptixExtendedDeferCollectKSweepConsensusTest(unittest.TestCase):
    def test_external_reviews_accept_goal1631_scope(self) -> None:
        claude = CLAUDE.read_text(encoding="utf-8")
        gemini = GEMINI.read_text(encoding="utf-8")

        self.assertIn("ACCEPTABLE", claude)
        self.assertIn("Blockers\n\nNone", claude)
        self.assertIn("approved", gemini)
        self.assertIn("Claim Boundaries", gemini)

    def test_consensus_preserves_narrow_claim_boundary(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("`ACCEPT`", text)
        self.assertIn("collect_k_test_module_count 108", text)
        self.assertIn("Ran 420 tests", text)
        self.assertIn("does not authorize public speedup wording", text)
        self.assertIn("true zero-copy wording", text)
        self.assertIn("stable `COLLECT_K_BOUNDED` promotion", text)
        self.assertIn("must not be quoted as copy-optimization", text)


if __name__ == "__main__":
    unittest.main()
