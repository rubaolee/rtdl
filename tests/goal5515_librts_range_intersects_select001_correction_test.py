from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"


class Goal5515RangeIntersectsSelect001CorrectionTest(unittest.TestCase):
    def test_historical_mismatches_are_zero_after_recheck(self) -> None:
        result = json.loads(
            (APP / "results" / "goal5515_range_intersects_select001_correction_gate.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(result["status"], "historical_select001_count_mismatches_no_longer_reproduced")
        self.assertEqual(result["current_case_count"], 6)
        self.assertEqual(result["current_match_count"], 5)
        self.assertEqual(result["current_author_capacity_failure_count"], 1)
        for case in result["historical_mismatch_recheck"]["cases"]:
            self.assertNotEqual(case["historical_delta"], 0)
            self.assertEqual(case["current_delta"], 0)

    def test_closeout_does_not_upgrade_claims(self) -> None:
        result = json.loads(
            (APP / "results" / "goal5515_range_intersects_select001_correction_gate.json").read_text(
                encoding="utf-8"
            )
        )
        boundary = result["claim_boundary"]
        self.assertTrue(boundary["historical_mismatch_resolution_evidence_only"])
        self.assertFalse(boundary["complete_range_intersects_matrix_claimed"])
        self.assertFalse(boundary["pointwise_intersection_equivalence_claimed"])
        self.assertFalse(boundary["performance_ratio_authorized"])
        self.assertFalse(boundary["complete_paper_reproduction_claimed"])


if __name__ == "__main__":
    unittest.main()
