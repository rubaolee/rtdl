import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GEMINI = ROOT / "docs" / "reviews" / "gemini_goal1656_kway_merge_probe_design_review_2026-05-10.md"


class Goal1656OptixCollectKKWayMergeDesignReviewTest(unittest.TestCase):
    def test_gemini_review_supports_probe_but_keeps_acceptance_strict(self) -> None:
        text = GEMINI.read_text(encoding="utf-8")

        self.assertIn("Yes", text)
        self.assertIn("4-way merge", text)
        self.assertIn("Deduplication", text)
        self.assertIn("Capacity Enforcement", text)
        self.assertIn("Register Pressure", text)
        self.assertIn("strict parity", text)
        self.assertNotIn("speedup measured", text.lower())


if __name__ == "__main__":
    unittest.main()
