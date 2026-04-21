import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GEMINI_REPORT = ROOT / "docs" / "reports" / "goal694_optix_rt_core_redesign_plan_2026-04-21.md"
CODEX_REVIEW = ROOT / "docs" / "reports" / "goal694_codex_review_of_gemini_rt_core_redesign_2026-04-21.md"
CLAUDE_REVIEW = ROOT / "docs" / "reports" / "goal694_claude_review_2026-04-21.md"


class Goal694RtCoreRedesignReviewTest(unittest.TestCase):
    def test_gemini_redesign_report_is_archived(self):
        self.assertTrue(GEMINI_REPORT.exists())
        text = GEMINI_REPORT.read_text(encoding="utf-8")
        self.assertIn("2.5D Orthogonal", text)
        self.assertIn("Outlier Detection", text)
        self.assertIn("DBSCAN", text)

    def test_codex_review_records_bounded_acceptance(self):
        self.assertTrue(CODEX_REVIEW.exists())
        text = CODEX_REVIEW.read_text(encoding="utf-8")
        for phrase in (
            "PARTIAL ACCEPT / ACCEPT WITH CORRECTIONS",
            "fixed-radius candidate generation",
            "exact refinement",
            "not a general nearest-neighbor",
            "Barnes-Hut is not implementation-ready",
            "remain `cuda_through_optix` today",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_first_implementation_target_is_fixed_radius_only(self):
        text = CODEX_REVIEW.read_text(encoding="utf-8")
        self.assertIn("fixed-radius neighbor count / threshold count", text)
        self.assertIn("Hausdorff, KNN/ANN, or Barnes-Hut RT-core rewrites", text)

    def test_claude_review_confirms_same_scope(self):
        self.assertTrue(CLAUDE_REVIEW.exists())
        text = CLAUDE_REVIEW.read_text(encoding="utf-8")
        for phrase in (
            "Outlier/DBSCAN fixed-radius counts only",
            "RT hardware does not enumerate misses",
            "No app should have its performance classification changed",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
