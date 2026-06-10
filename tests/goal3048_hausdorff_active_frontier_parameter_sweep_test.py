from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt
from examples.current.research_benchmarks.hausdorff_xhd import rtdl_hausdorff_v2_function as hd


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "goal3048_hausdorff_active_frontier_parameter_sweep.py"
REPORT = REPO_ROOT / "docs" / "reports" / "goal3048_hausdorff_active_frontier_parameter_sweep_2026-06-02.md"
ARTIFACT = REPO_ROOT / "docs" / "reports" / "goal3048_hausdorff_active_frontier_parameter_sweep_a4000_2026-06-02.json"
LANGUAGE_LAB = REPO_ROOT / "examples" / "v2_0" / "research_benchmarks" / "hausdorff_xhd" / "rtdl_hausdorff_v2_language_lab.py"


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
            "A4000 run passed",
            "active-frontier defaults promoted to seed 1024 and group floor 512",
            "`seed_sample_count=8192` was never the best configuration",
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

    def test_a4000_artifact_supports_narrow_seed_default_but_not_claims(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["goal"], "Goal3048")
        self.assertEqual(data["seed_sample_counts"], [512, 1024, 2048, 8192])
        self.assertEqual(data["target_points_per_groups"], [512, 1024, 2048])
        self.assertEqual(data["current_seed_sample_count"], 1024)
        self.assertEqual(data["current_target_points_per_group"], 512)
        self.assertTrue(data["all_rows_match_distance"])
        self.assertEqual(len(data["rows"]), 8)
        self.assertGreater(data["best_config_frequency"]["seed_1024_group_1024"], 0)
        self.assertEqual(data["best_config_frequency"]["seed_8192_group_512"], 0)
        self.assertEqual(data["best_config_frequency"]["seed_8192_group_1024"], 0)
        self.assertEqual(data["best_config_frequency"]["seed_8192_group_2048"], 0)
        self.assertLess(data["median_best_vs_current_policy_median_ratio"], 1.0)
        self.assertFalse(data["default_policy_change_authorized"])
        self.assertFalse(data["public_speedup_claim_authorized"])
        self.assertFalse(data["rt_core_speedup_claim_authorized"])

    def test_active_frontier_default_seed_matches_measured_policy(self) -> None:
        function_source = (
            REPO_ROOT
            / "examples"
            / "v2_0"
            / "research_benchmarks"
            / "hausdorff_xhd"
            / "rtdl_hausdorff_v2_function.py"
        ).read_text(encoding="utf-8")
        lab_source = LANGUAGE_LAB.read_text(encoding="utf-8")

        self.assertEqual(hd.DEFAULT_ACTIVE_FRONTIER_SEED_SAMPLE_COUNT, 1024)
        self.assertIn("DEFAULT_ACTIVE_FRONTIER_SEED_SAMPLE_COUNT = 1024", function_source)
        self.assertIn(
            "seed_sample_count: int = DEFAULT_ACTIVE_FRONTIER_SEED_SAMPLE_COUNT",
            function_source,
        )
        self.assertIn(
            "group_size_ab = _resolve_adaptive_target_points_per_group(columns_b, target_points_per_group)",
            function_source,
        )
        self.assertIn(
            "group_size_ba = _resolve_adaptive_target_points_per_group(columns_a, target_points_per_group)",
            function_source,
        )
        self.assertIn("default=hd.DEFAULT_ACTIVE_FRONTIER_SEED_SAMPLE_COUNT", lab_source)

    def test_v2_6_roadmap_indexes_parameter_sweep_without_public_claims(self) -> None:
        roadmap = rt.v2_6_roadmap()
        validation = rt.validate_v2_6_roadmap(repo_root=REPO_ROOT)

        self.assertEqual(roadmap["hausdorff_active_frontier_parameter_sweep_goal"], "Goal3048")
        self.assertIn("seed_default_1024", roadmap["hausdorff_active_frontier_parameter_sweep_status"])
        self.assertIn("group_floor_512", roadmap["hausdorff_active_frontier_parameter_sweep_status"])
        self.assertIn("not_public_speedup_evidence", roadmap["hausdorff_active_frontier_parameter_sweep_status"])
        self.assertFalse(roadmap["release_authorized"])
        self.assertFalse(roadmap["public_speedup_claim_authorized"])
        self.assertEqual("accept", validation["status"])


if __name__ == "__main__":
    unittest.main()
