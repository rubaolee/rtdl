from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


SUMMARY = ROOT / "future" / "v4" / "evidence" / "v4_goal4665_hausdorff_focused_20260625" / "summary.json"
REPORT = ROOT / "future" / "v4" / "v4_goal4665_hausdorff_focused_formal_candidate_run_2026-06-25.md"


class V4Goal4665HausdorffFocusedCandidateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_focused_run_fails_formal_bar(self) -> None:
        self.assertEqual(
            "goal4665_hausdorff_focused_run_complete_failed_formal_bar",
            self.summary["status"],
        )
        self.assertEqual(
            "hausdorff_formal_candidate_fails_focused_bar",
            self.summary["decision"]["label"],
        )
        self.assertFalse(self.summary["decision"]["may_count_as_formal_high_performance_v4_evidence"])
        self.assertFalse(self.summary["decision"]["may_trigger_full_all_app_rerun"])
        self.assertFalse(self.summary["claim_boundary"]["release_authorized"])
        self.assertFalse(self.summary["claim_boundary"]["formal_high_performance_v4_authorized"])
        self.assertFalse(self.summary["claim_boundary"]["whole_app_speedup_claim_authorized"])

    def test_serious_scale_failure_is_visible(self) -> None:
        rows = {row["points_per_side"]: row for row in self.summary["rows"]}

        self.assertIn(65536, rows)
        self.assertIn(262144, rows)
        self.assertTrue(rows[65536]["passes_v4_vs_v3_hot_bar"])
        self.assertFalse(rows[65536]["passes_prepare_floor"])
        self.assertFalse(rows[262144]["passes_v4_vs_v3_hot_bar"])
        self.assertFalse(rows[262144]["passes_prepare_floor"])
        self.assertLess(rows[262144]["speedup_v4_hot_over_v3_0_2_hot"], 1.0)
        self.assertTrue(rows[262144]["passes_v4_vs_v2_primary_bar"])
        self.assertTrue(rows[262144]["passes_correctness"])

    def test_large_scale_correctness_probe_is_not_speed_claim(self) -> None:
        probe = self.summary["large_scale_correctness_probe"]

        self.assertEqual(262144, probe["copies"])
        self.assertEqual(1048576, probe["points_per_side"])
        self.assertTrue(probe["matches_oracle"])
        self.assertTrue(probe["coordinate_normalization_used"])
        self.assertEqual(1000000.0, probe["coordinate_normalization_span"])
        self.assertFalse(self.summary["claim_boundary"]["unrestricted_exact_hausdorff_claim_authorized"])

    def test_report_names_failure_and_next_engineering_need(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("fails formal bar", text)
        self.assertIn("the serious 262,144-point row fails", text)
        self.assertIn("certify a V4 CuPy continuation/front door", text)
        self.assertIn("does not authorize V4 release", text)


if __name__ == "__main__":
    unittest.main()
