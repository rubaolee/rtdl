from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal3024_hausdorff_optix_group_sweep_2026-06-02.md"
ARTIFACT = REPO_ROOT / "docs" / "reports" / "goal3024_hausdorff_optix_group_sweep_2026-06-02.json"


class Goal3024HausdorffOptixGroupSweepTest(unittest.TestCase):
    def test_report_records_negative_tuning_result(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3024",
            "simple parameter change",
            "The answer is no",
            "0.7740153260529041",
            "1.0035458281636238",
            "0.003780316561460495",
            "closes the cheap-tuning branch",
            "not permission to add Hausdorff-specific native engine logic",
            "does not authorize v2.6 release",
        ):
            self.assertIn(phrase, text)

    def test_artifact_records_best_rows_and_boundaries(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(data["goal"], "Goal3024")
        self.assertEqual(data["source_commit"], "bc9b6dc670886c7491aa0dcd70fae9d7a237402b")
        self.assertEqual(data["source_dirty"], [])
        self.assertEqual(data["gpu"], "NVIDIA L4, 565.57.01")
        self.assertEqual(data["cuda_prefix"], "/usr/local/cuda-12.6")
        self.assertEqual(data["point_count_a"], 4096)
        self.assertEqual(data["point_count_b"], 4096)
        self.assertFalse(data["parameter_tuning_solves_gap"])
        self.assertIn("next_step_requires_richer_generic_candidate_frontier", data["finding"])

        best_adaptive = data["best_adaptive"]
        self.assertEqual(best_adaptive["target_points_per_group"], 512)
        self.assertAlmostEqual(best_adaptive["elapsed_sec"], 0.7740153260529041)
        self.assertEqual(best_adaptive["threshold_iterations"], 4)
        self.assertTrue(best_adaptive["rt_core_accelerated"])

        best_reduced = data["best_reduced_no_threshold"]
        self.assertEqual(best_reduced["target_points_per_group"], 64)
        self.assertAlmostEqual(best_reduced["elapsed_sec"], 1.0035458281636238)
        self.assertEqual(best_reduced["threshold_iterations"], 0)
        self.assertGreater(best_reduced["elapsed_sec"], best_adaptive["elapsed_sec"])

        self.assertEqual(len(data["rows"]), 16)
        for row in data["rows"]:
            self.assertTrue(row["rt_core_accelerated"])
            self.assertAlmostEqual(row["distance"], 0.13528455701336056)

        for field in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "app_specific_native_engine_logic_authorized",
        ):
            self.assertFalse(data[field])

    def test_v2_6_roadmap_indexes_goal3024(self) -> None:
        roadmap = rt.v2_6_roadmap()
        self.assertEqual(roadmap["hausdorff_optix_group_sweep_goal"], "Goal3024")
        self.assertIn("cheap_tuning_does_not_close_gap", roadmap["hausdorff_optix_group_sweep_status"])
        self.assertIn("not_speedup_evidence", roadmap["hausdorff_optix_group_sweep_status"])
        validation = rt.validate_v2_6_roadmap(repo_root=REPO_ROOT)
        self.assertEqual("accept", validation["status"])


if __name__ == "__main__":
    unittest.main()
