from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal1938_gemini_review_goal1937_repeat3_fixed_radius_2026-05-13.md"
REPORT = ROOT / "docs" / "reports" / "goal1937_fixed_radius_repeat3_pod_perf_2026-05-13.md"
LOG = ROOT / "docs" / "reports" / "goal1937_fixed_radius_repeat3_pod" / "run.log"


class Goal1938GeminiReviewGoal1937Repeat3FixedRadiusTest(unittest.TestCase):
    def test_review_accepts_with_boundary(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Overall Verdict: `accept-with-boundary`", text)
        self.assertIn("single-repeat caveat", text)
        self.assertIn("all 12 fixed-radius rows", text)
        self.assertIn("no v2.0 release authorization", text)
        self.assertIn("Missing Git Metadata", text)

    def test_report_records_review_and_log_is_tracked(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Gemini Goal1938", text)
        self.assertIn("source_commit_label: unknown", text)
        self.assertIn("run log is tracked", text)
        self.assertTrue(LOG.exists())


if __name__ == "__main__":
    unittest.main()
