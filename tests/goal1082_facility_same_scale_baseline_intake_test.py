from __future__ import annotations

import unittest

from scripts.goal1082_facility_same_scale_baseline_intake import build_intake
from scripts.goal1082_facility_same_scale_baseline_intake import to_markdown


class Goal1082FacilitySameScaleBaselineIntakeTest(unittest.TestCase):
    def test_same_scale_intake_blocks_public_claim(self) -> None:
        intake = build_intake()

        self.assertTrue(intake["valid"])
        self.assertEqual(intake["verdict"], "BLOCK")
        self.assertTrue(intake["checks"]["same_scale"])
        self.assertFalse(intake["checks"]["decision_matches"])
        self.assertFalse(intake["checks"]["covered_count_matches"])
        self.assertFalse(intake["checks"]["public_claim_authorized"])

    def test_records_exact_mismatch_counts(self) -> None:
        intake = build_intake()

        self.assertEqual(intake["scale"]["copies"], 2_500_000)
        self.assertEqual(intake["scale"]["query_count"], 10_000_000)
        self.assertEqual(intake["rtx_result"]["threshold_reached_count"], 8_898_102)
        self.assertEqual(intake["baseline_result"]["covered_customer_count"], 10_000_000)
        self.assertTrue(intake["rtx_result"]["skip_validation"])

    def test_markdown_keeps_honesty_boundary(self) -> None:
        markdown = to_markdown(build_intake())

        self.assertIn("Verdict: **BLOCK**", markdown)
        self.assertIn("does not authorize public RTX speedup claims", markdown)
        self.assertIn("precision", markdown)


if __name__ == "__main__":
    unittest.main()
