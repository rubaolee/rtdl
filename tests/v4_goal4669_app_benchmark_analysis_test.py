from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_app_benchmark_analysis import analyze_goal4654_summary  # noqa: E402


class V4Goal4669AppBenchmarkAnalysisTest(unittest.TestCase):
    def _summary(self, *, probe: bool) -> dict[str, object]:
        return {
            "schema": "rtdl.v4.goal4669.full_app_level_pod_benchmark_after_hausdorff.v1",
            "status": "goal4669_evidence_collected_not_release",
            "analysis": {
                "formal_tag_native_optix_purity": True,
                "app_scorecard": [
                    {
                        "app": "hausdorff_xhd",
                        "all_returncode_zero": True,
                        "all_correctness_parity_or_skipped_oracle": True,
                        "coordinate_normalized_1m_correctness_probe_passed": probe,
                        "v4_vs_v2_14_hot_speedup": 120.0,
                        "v4_vs_v3_0_2_hot_speedup": 1.30,
                        "v3_0_2_vs_v2_14_hot_speedup": 90.0,
                        "v4_vs_v2_14_primary_wall_speedup": 1.35,
                        "v4_prepare_vs_v3_0_2_speedup": 0.90,
                    }
                ],
            },
            "claim_boundary": {
                "release_authorized": False,
                "public_speedup_claim_authorized": False,
                "partner_migration_counts_as_v4_speed_win": False,
            },
        }

    def test_hausdorff_passes_only_with_custom_bar_and_probe(self) -> None:
        analysis = analyze_goal4654_summary(self._summary(probe=True))
        row = analysis["app_rows"][0]

        self.assertEqual("true_v4_operator_win_candidate", row["claim_class"])
        self.assertTrue(row["pass_frozen_speed_bar"])
        self.assertTrue(row["contributes_to_formal_high_performance"])
        self.assertEqual(1, analysis["true_v4_candidate_app_count"])

    def test_hausdorff_missing_probe_is_blocked_even_when_speed_ratios_are_high(self) -> None:
        analysis = analyze_goal4654_summary(self._summary(probe=False))
        row = analysis["app_rows"][0]

        self.assertEqual("blocked_missing_metric_or_correctness", row["claim_class"])
        self.assertFalse(row["pass_frozen_speed_bar"])
        self.assertFalse(row["contributes_to_formal_high_performance"])
        self.assertIn("1M correctness-boundary probe", row["explanation"])


if __name__ == "__main__":
    unittest.main()
