from __future__ import annotations

import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_app_benchmark_analysis import analyze_goal4654_summary  # noqa: E402
from rtdsl.v4_app_benchmark_analysis import load_goal4654_summary  # noqa: E402

SUMMARY = ROOT / "future" / "v4" / "evidence" / "v4_goal4654_serious_20260625_2" / "summary.json"


class V4Goal4655AppBenchmarkAnalysisTest(unittest.TestCase):
    def setUp(self) -> None:
        self.summary = load_goal4654_summary(SUMMARY)
        self.analysis = analyze_goal4654_summary(self.summary)

    def test_decision_blocks_formal_high_performance_claim(self) -> None:
        self.assertEqual(
            "bounded_operator_v4_only__app_level_high_performance_not_supported",
            self.analysis["decision_label"],
        )
        self.assertFalse(self.analysis["formal_high_performance_v4_supported"])
        self.assertTrue(self.analysis["bounded_operator_v4_only"])
        self.assertIn(
            "old_version_optix_uses_v4_compatibility_native_library",
            self.analysis["blocking_reasons"],
        )

    def test_partner_and_release_claim_locks_are_preserved(self) -> None:
        self.assertTrue(self.analysis["partner_migration_lock_preserved"])
        boundary = self.analysis["claim_boundary"]
        self.assertFalse(boundary["release_authorized"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])
        self.assertFalse(boundary["whole_app_high_performance_claim_authorized"])
        self.assertFalse(boundary["partner_migration_counts_as_v4_speed_win"])

    def test_rows_are_classified_without_overclaiming_triangle(self) -> None:
        rows = {row["app"]: row for row in self.analysis["app_rows"]}
        self.assertEqual(
            "modest_runtime_gain_below_formal_bar",
            rows["rt_dbscan"]["claim_class"],
        )
        self.assertEqual("parity_not_v4_speed_win", rows["raydb_style"]["claim_class"])
        self.assertEqual("parity_not_v4_speed_win", rows["librts_spatial_index"]["claim_class"])
        self.assertEqual(
            "historical_route_evolution_plus_modest_v4_increment",
            rows["triangle_counting"]["claim_class"],
        )
        self.assertTrue(rows["triangle_counting"]["pass_frozen_speed_bar"])
        self.assertFalse(rows["triangle_counting"]["contributes_to_formal_high_performance"])

    def test_source_evidence_was_complete_enough_for_analysis(self) -> None:
        self.assertTrue(self.summary["analysis"]["all_rows_returncode_zero"])
        self.assertTrue(self.summary["analysis"]["all_rows_json_parse_ok"])
        self.assertTrue(self.summary["analysis"]["all_full_rows_have_hot_metric"])


if __name__ == "__main__":
    unittest.main()
