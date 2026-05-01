from __future__ import annotations

import unittest

from scripts.goal1108_current_rtx_vs_baseline_comparison import build_comparison
from scripts.goal1108_current_rtx_vs_baseline_comparison import to_markdown


class Goal1108CurrentRtxVsBaselineComparisonTest(unittest.TestCase):
    def test_current_artifacts_compare_but_do_not_authorize_public_claims(self) -> None:
        payload = build_comparison()

        self.assertTrue(payload["valid"])
        self.assertEqual(payload["summary"]["row_count"], 2)
        self.assertEqual(payload["summary"]["public_speedup_claim_authorized_count"], 0)
        for row in payload["rows"]:
            self.assertEqual(row["rtx_status"], "ok")
            self.assertFalse(row["public_speedup_claim_authorized"])
            self.assertIn("cross_host_comparison_not_public_claim", row["public_claim_blockers"])
            self.assertIn("public_wording_review_required", row["public_claim_blockers"])
            self.assertGreater(float(row["rtx_query_median_sec"]), 0.0)
            for baseline in row["baselines"]:
                self.assertEqual(baseline["status"], "ok")
                self.assertGreater(float(baseline["native_query_median_sec"]), 0.0)
                self.assertGreater(float(baseline["engineering_ratio_baseline_over_rtx"]), 0.0)

    def test_barnes_hut_uses_radius_matched_baseline(self) -> None:
        payload = build_comparison()
        barnes = next(row for row in payload["rows"] if row["app"] == "barnes_hut_force_app")

        self.assertEqual(barnes["rtx_validation_status"], "ok")
        self.assertEqual(len(barnes["baselines"]), 1)
        self.assertEqual(barnes["baselines"][0]["baseline"], "embree")
        self.assertGreater(barnes["baselines"][0]["engineering_ratio_baseline_over_rtx"], 100.0)

    def test_markdown_preserves_engineering_only_boundary(self) -> None:
        markdown = to_markdown(build_comparison())

        self.assertIn("Goal1108 Current RTX vs Same-Contract Baseline Comparison", markdown)
        self.assertIn("engineering comparison ratios", markdown)
        self.assertIn("does not authorize public RTX speedup claims", markdown)
        self.assertIn("cross_host_comparison_not_public_claim", markdown)


if __name__ == "__main__":
    unittest.main()
