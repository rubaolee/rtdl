from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1923_claude_post_pod_review_integration_2026-05-13.md"
REVIEW = ROOT / "docs" / "reviews" / "goal1912_claude_review_goal1903_post_pod_artifacts_2026-05-13.md"
READINESS = ROOT / "docs" / "reports" / "goal1911_v2_readiness_aggregator.json"


class Goal1923ClaudePostPodReviewIntegrationTest(unittest.TestCase):
    def test_report_and_claude_review_close_decisive_review_blocker(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        review = REVIEW.read_text(encoding="utf-8")
        readiness = json.loads(READINESS.read_text(encoding="utf-8"))

        self.assertIn("Status: decisive-post-pod-review-complete-release-still-blocked", report)
        self.assertIn("`accept-with-boundary`", report)
        self.assertIn("fixed-radius does not authorize", report)
        self.assertIn("partner_output_columns_true_zero_copy_authorized: true", report)
        self.assertIn("final v2.0 release consensus", report)

        self.assertIn("Verdict", review)
        self.assertIn("accept-with-boundary", review)
        self.assertIn("Fixed-radius", review)
        self.assertIn("True-zero-copy claim: NOT supported for fixed-radius", review)

        self.assertIn(
            "docs/reviews/goal1912_claude_review_goal1903_post_pod_artifacts_2026-05-13.md",
            readiness["decisive_post_pod_review_files"],
        )
        self.assertNotIn(
            "fresh Claude or Pro-class review of actual pod artifacts missing",
            readiness["blockers"],
        )
        self.assertFalse(readiness["claim_boundary"]["v2_0_release_authorized"])


if __name__ == "__main__":
    unittest.main()
