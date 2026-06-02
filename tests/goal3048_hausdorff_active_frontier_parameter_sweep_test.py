from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "goal3048_hausdorff_active_frontier_parameter_sweep.py"
REPORT = REPO_ROOT / "docs" / "reports" / "goal3048_hausdorff_active_frontier_parameter_sweep_2026-06-02.md"


class Goal3048HausdorffActiveFrontierParameterSweepTest(unittest.TestCase):
    def test_report_records_tuning_scope_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3048",
            "seed sample count",
            "target points per group",
            "cupy_grouped_grid_rawkernel",
            "seed_sample_count=1024",
            "target_points_per_group=512",
            "does not authorize",
            "automatic default-policy change",
        ):
            self.assertIn(phrase, text)

    def test_script_sweeps_seed_and_group_policy_without_claims(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "goal3046_hausdorff_active_frontier_dataset_diversity",
            "seed_sample_counts",
            "target_points_per_groups",
            "current_policy_config",
            "best_vs_current_policy_median_ratio",
            "best_config_frequency",
            "all_rows_match_distance",
            '"default_policy_change_authorized": False',
            '"public_speedup_claim_authorized": False',
            '"rt_core_speedup_claim_authorized": False',
            '"true_zero_copy_claim_authorized": False',
        ):
            self.assertIn(phrase, source)


if __name__ == "__main__":
    unittest.main()
