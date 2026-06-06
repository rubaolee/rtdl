from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CLAUDE = ROOT / "docs" / "reviews" / "goal3576_claude_review_goal3575_raydb_stats_mode_2026-06-06.md"
GEMINI = ROOT / "docs" / "reviews" / "goal3577_gemini_review_goal3575_raydb_stats_mode_2026-06-06.md"


class Goal3576Goal3577ExternalReviewsGoal3575Test(unittest.TestCase):
    def test_claude_review_accepts_goal3575_with_claim_boundary(self) -> None:
        text = CLAUDE.read_text(encoding="utf-8")
        self.assertIn("Reviewer: Claude", text)
        self.assertIn("Verdict: **accept**", text)
        self.assertIn("group_stats_i64", text)
        self.assertIn("PAPER_RT_RESULT_MODES", text)
        self.assertIn("generic_stats_abi_used: true", text)
        self.assertIn("No overclaims", text)
        self.assertIn("no release or public", text)

    def test_gemini_review_accepts_with_boundary_and_exact_artifact_fields(self) -> None:
        text = GEMINI.read_text(encoding="utf-8")
        self.assertIn("Verdict:** `accept-with-boundary`", text)
        self.assertIn("row count:** `960000`", text)
        self.assertIn("matches CPU reference:** `true`", text)
        self.assertIn("native launch count:** `1`", text)
        self.assertIn("generic stats ABI used:** `true`", text)
        self.assertIn("query median sec:** `0.000477436930`", text)
        self.assertIn("true zero-copy claim:** `false`", text)
        self.assertIn("does not authorize a release or public claim", text)


if __name__ == "__main__":
    unittest.main()
