from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "reviews" / "goal1936_claude_review_goal1933_1935_large_scale_perf_2026-05-13.md"
REPORT = ROOT / "docs" / "reports" / "goal1933_goal1934_large_scale_all_app_v2_pod_perf_2026-05-13.md"


class Goal1936ClaudeReviewGoal1933Goal1935LargeScalePerfTest(unittest.TestCase):
    def test_review_accepts_with_boundary_and_records_caveats(self) -> None:
        text = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Overall Verdict: `accept-with-boundary`", text)
        self.assertIn("Fixed-radius 524288 re-run should use `repeat >= 3`", text)
        self.assertIn("Artifact provenance", text)
        self.assertIn("DB phase totals schema issue", text)
        self.assertIn("rt_core_accelerated: false", text)
        self.assertIn("The review is acceptable as a distinct external review", text)

    def test_report_carries_claude_boundaries_forward(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Claude Goal1936", text)
        self.assertIn("single-sample", text)
        self.assertIn("reused provenance", text)
        self.assertIn("phase-total aggregation", text)
        self.assertIn("polygon control rows do not activate RT cores", text)


if __name__ == "__main__":
    unittest.main()
