from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs" / "reports" / "goal2811_rtnn_density_aware_direct_aggregate_2026-05-31.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2811_rtnn_direct_density_aggregate_pod"
ARTIFACT_32768 = ARTIFACT_DIR / "rtnn_direct_density_median_f32_32768.json"
ARTIFACT_65536 = ARTIFACT_DIR / "rtnn_direct_density_median_f32_65536.json"
EXPECTED_COMMIT = "4de076381c6012ee1d9e62e14a8d8d44399109ba"


class Goal2811RtnnDirectAggregateKernelTest(unittest.TestCase):
    def test_direct_kernel_is_generic_fixed_radius_aggregate(self) -> None:
        core = CORE.read_text(encoding="utf-8")

        self.assertIn("fixed_radius_neighbors_3d_grid_ranked_summary_aggregate_f32_direct", core)
        self.assertIn("const GpuPoint3D* query_points", core)
        self.assertIn("FrnRankedAggregate* aggregate_out", core)
        self.assertIn("frn_ranked_insert_f32", core)
        self.assertIn("local_nearest_checksum += 0xffffffffull", core)
        self.assertNotIn("rtnn", core.lower())

    def test_promoted_float32_path_has_density_aware_direct_and_fallback_paths(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        runtime = (ROOT / "src" / "rtdsl" / "optix_runtime.py").read_text(encoding="utf-8")
        direct_name = "fixed_radius_neighbors_3d_grid_ranked_summary_aggregate_f32_direct"

        self.assertIn("occupied_cell_count", workloads)
        self.assertIn("mean_search_points_per_occupied_cell", workloads)
        self.assertIn("mean_search_points_per_occupied_cell <= 4.0", workloads)
        self.assertIn("use_direct_float32_aggregate ? 12u : use_float32_precision ? 11u : 10u", workloads)
        self.assertIn("g_frn3d_grid_ranked_summary_aggregate_f32_direct", workloads)
        self.assertIn(f'cuModuleGetFunction(&g_frn3d_grid_ranked_summary_aggregate_f32_direct.fn, g_frn3d_grid.module, "{direct_name}")', workloads)
        self.assertIn("cuLaunchKernel(g_frn3d_grid_ranked_summary_aggregate_f32_direct.fn", workloads)
        self.assertIn("cuLaunchKernel(g_frn3d_grid_ranked_summary_f32.fn", workloads)
        self.assertIn("&d_aggregate.ptr", workloads)
        self.assertIn('12: "prepared_uniform_cell_ranked_summary_aggregate_f32_direct"', runtime)

    def test_pod_artifacts_are_clean_and_median_timed(self) -> None:
        for artifact in (ARTIFACT_32768, ARTIFACT_65536):
            payload = json.loads(artifact.read_text(encoding="utf-8"))
            with self.subTest(artifact=artifact.name):
                self.assertEqual(payload["status"], "pass")
                self.assertEqual(payload["source_commit"], EXPECTED_COMMIT)
                self.assertEqual(payload["source_dirty"], [])
                self.assertIn("v4.aggregate_float32_median", payload["harness_version"])
                modes = {mode for row in payload["rows"] for mode in row["rtdl_phase_summary"]["modes"]}
                self.assertIn("prepared_uniform_cell_ranked_summary_aggregate_f32_direct", modes)
                self.assertIn("prepared_uniform_cell_ranked_summary_aggregate_f32", modes)
                for row in payload["rows"]:
                    self.assertEqual(row["status"], "pass")
                    self.assertEqual(row["rtdl_elapsed_statistic"], "median")
                    self.assertEqual(row["cupy_grid_elapsed_statistic"], "median")
                    self.assertTrue(row["ranked_aggregate_matches_cupy_grid"])
                    self.assertLess(float(row["cupy_grid_over_rtdl_elapsed_ratio"]), 1.0)

    def test_report_keeps_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("accept-with-boundary", report)
        self.assertIn("density signal without naming RTNN", report)
        self.assertIn("No RTDL-beats-CuPy claim is authorized", report)
        self.assertIn("one small regression is the 65K shell row", report)
        self.assertIn("generic cooperative/tiled top-k reducer", report)


if __name__ == "__main__":
    unittest.main()
