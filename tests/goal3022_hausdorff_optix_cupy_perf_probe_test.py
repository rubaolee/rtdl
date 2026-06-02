from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal3022_hausdorff_optix_cupy_perf_probe_2026-06-02.md"
ARTIFACT = REPO_ROOT / "docs" / "reports" / "goal3022_hausdorff_optix_cupy_perf_probe_2026-06-02.json"


class Goal3022HausdorffOptixCupyPerfProbeTest(unittest.TestCase):
    def test_report_records_perf_gap_without_claim_leak(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3022",
            "CuPy: `14.1.1`",
            "RT Cores",
            "rtdl_rt_grouped_adaptive_nearest_witness",
            "cupy_grouped_grid_rawkernel",
            "232.36649959218957x",
            "current dense exact Hausdorff performance favors the explicit CuPy partner path",
            "not an RTDL correctness failure",
            "must not become Hausdorff-specific native-engine customizations",
            "does not authorize v2.6 release",
        ):
            self.assertIn(phrase, text)

    def test_artifact_records_exact_rt_rows_and_cupy_winner(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(data["goal"], "Goal3022")
        self.assertEqual(data["source_commit"], "220971c0361b4fcab13571580ffa7889219b5e3c")
        self.assertEqual(data["source_dirty"], [])
        self.assertEqual(data["gpu"], "NVIDIA L4, 565.57.01")
        self.assertEqual(data["cuda_prefix"], "/usr/local/cuda-12.6")
        self.assertEqual(data["cupy_version"], "14.1.1")
        self.assertEqual(data["numba_version"], "0.65.1")
        self.assertEqual(data["best_current_rt_method"], "rtdl_rt_grouped_adaptive_nearest_witness")
        self.assertEqual(data["best_current_non_rt_partner_method"], "cupy_grouped_grid_rawkernel")
        self.assertTrue(data["all_rt_rows_exact_and_rt_core"])
        self.assertTrue(data["all_recorded_parity_true"])
        self.assertIn("cupy_grouped_grid_is_current_fast_reference_partner_path", data["design_finding"])

        rows = data["rows"]
        adaptive_4096 = next(
            row for row in rows
            if row["method"] == "rtdl_rt_grouped_adaptive_nearest_witness" and row["points"] == 4096
        )
        cupy_4096 = next(
            row for row in rows
            if row["method"] == "cupy_grouped_grid_rawkernel" and row["points"] == 4096
        )
        self.assertTrue(adaptive_4096["rt_core_accelerated"])
        self.assertEqual(adaptive_4096["threshold_iterations"], 4)
        self.assertGreater(adaptive_4096["primary_vs_cupy_ratio"], 200.0)
        self.assertLess(cupy_4096["primary_elapsed_sec"], 0.01)

        for field in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "package_install_claim_authorized",
        ):
            self.assertFalse(data[field])

    def test_v2_6_roadmap_indexes_goal3022(self) -> None:
        roadmap = rt.v2_6_roadmap()
        self.assertEqual(roadmap["hausdorff_optix_cupy_perf_probe_goal"], "Goal3022")
        self.assertIn("cupy_grouped_grid_current_fast_reference", roadmap["hausdorff_optix_cupy_perf_probe_status"])
        self.assertIn("not_speedup_evidence", roadmap["hausdorff_optix_cupy_perf_probe_status"])
        validation = rt.validate_v2_6_roadmap(repo_root=REPO_ROOT)
        self.assertEqual("accept", validation["status"])


if __name__ == "__main__":
    unittest.main()
