import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal3991_gemini_review_goal3990_dense_grouped_union_design_2026-06-08.md"
HANDOFF = ROOT / "docs" / "handoff" / "HANDOFF_GEMINI_GOAL3990_DENSE_GROUPED_UNION_DESIGN_2026-06-08.md"


class Goal3991GeminiReviewGoal3990DenseGroupedUnionDesignTest(unittest.TestCase):
    def test_review_exists_with_accepted_boundary_verdict(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")
        self.assertIn("Independent Gemini Review", text)
        self.assertIn("Goal3990 Dense Fixed-Radius Grouped Union", text)
        self.assertIn("accept-with-boundary", text)

    def test_review_reinforces_core_boundaries(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")
        for fragment in [
            "app-agnostic primitive boundary",
            "deterministic component-root policy",
            "staleness/convergence metadata",
            "parity tests",
            "avoid overclaiming release readiness",
            "automatic backend selection",
        ]:
            self.assertIn(fragment, text)

    def test_handoff_names_required_review_questions(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")
        for fragment in [
            "existing route toggles and partner substitution are exhausted",
            "DBSCAN/clustering policy kept outside native ABI",
            "dense/sparse pod evidence",
            "app-specific engine logic",
        ]:
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()

