from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"


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


if __name__ == "__main__":
    unittest.main()
