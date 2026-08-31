from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal3025_hausdorff_adaptive_reduced_pod_probe_2026-06-02.md"
ARTIFACT = REPO_ROOT / "docs" / "reports" / "goal3025_hausdorff_adaptive_reduced_pod_probe_2026-06-02.json"


class Goal3025HausdorffAdaptiveReducedPodProbeTest(unittest.TestCase):
    def test_report_records_negative_probe_without_claim_leak(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3025",
            "threshold_flags",
            "nearest_max_distance_row",
            "No native Hausdorff-specific ABI or kernel was added",
            "1.2940954267978668",
            "0.7740153260529041",
            "Do not promote",
            "useful negative design evidence",
            "generic device-resident active-set compaction",
            "does not authorize",
        ):
            self.assertIn(phrase, text)

    def test_artifact_records_correct_but_slower_result(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(data["goal"], "Goal3025")
        self.assertEqual(data["source_commit"], "f0f0253f1fa928ff3a4ba4929ebdf0eb77913c45")
        self.assertEqual(data["source_dirty"], [])
        self.assertEqual(data["gpu"], "NVIDIA L4, 565.57.01")
        self.assertEqual(data["cuda_prefix"], "/usr/local/cuda-12.6")
        self.assertEqual(data["method"], "rtdl_rt_grouped_adaptive_reduced_nearest_witness")
        self.assertTrue(data["correctness_passed"])
        self.assertFalse(data["promote_as_recommended_rt_path"])
        self.assertIn("do_not_promote_adaptive_reduced_method", data["finding"])

        self.assertEqual(data["known_better_current_rt_method"], "rtdl_rt_grouped_adaptive_nearest_witness_target_group_512")
        self.assertAlmostEqual(data["known_better_current_rt_4096_sec"], 0.7740153260529041)

        rows = data["rows"]
        self.assertEqual([row["points"] for row in rows], [512, 4096])
        row_512 = rows[0]
        row_4096 = rows[1]
        self.assertTrue(row_512["rt_core_accelerated"])
        self.assertTrue(row_512["cupy_matches_primary"])
        self.assertAlmostEqual(row_512["primary_elapsed_sec"], 1.3788113221526146)
        self.assertEqual(row_512["threshold_iterations"], 2)
        self.assertTrue(row_4096["rt_core_accelerated"])
        self.assertTrue(row_4096["cupy_matches_primary"])
        self.assertAlmostEqual(row_4096["primary_elapsed_sec"], 1.2940954267978668)
        self.assertEqual(row_4096["threshold_iterations"], 4)
        self.assertGreater(row_4096["primary_elapsed_sec"], data["known_better_current_rt_4096_sec"])
        self.assertGreater(row_4096["primary_vs_cupy_ratio"], 300.0)

        for field in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "app_specific_native_engine_logic_authorized",
        ):
            self.assertFalse(data[field])

    def test_v2_6_roadmap_indexes_goal3025_probe(self) -> None:
        roadmap = rt.v2_6_roadmap()
        self.assertEqual(roadmap["hausdorff_adaptive_reduced_probe_goal"], "Goal3025")
        self.assertIn("correct_but_slower", roadmap["hausdorff_adaptive_reduced_probe_status"])
        self.assertIn("not_promoted", roadmap["hausdorff_adaptive_reduced_probe_status"])
        validation = rt.validate_v2_6_roadmap(repo_root=REPO_ROOT)
        self.assertEqual("accept", validation["status"])


if __name__ == "__main__":
    unittest.main()
