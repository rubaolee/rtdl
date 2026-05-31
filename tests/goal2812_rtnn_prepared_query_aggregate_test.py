from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
RUNNER = ROOT / "scripts" / "goal2348_rtnn_v2_2_external_runner.py"
HARNESS = ROOT / "scripts" / "goal2800_rtnn_v25_live_ranked_summary_harness.py"


class Goal2812RtnnPreparedQueryAggregateTest(unittest.TestCase):
    def test_native_abi_exposes_generic_prepared_query_path(self) -> None:
        api = API.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("PreparedFixedRadiusQueryPoints3D", workloads)
        self.assertIn("prepare_fixed_radius_query_points_grid_3d_optix", workloads)
        self.assertIn("aggregate_prepared_query_ranked_fixed_radius_neighbor_summaries_grid_3d_optix", workloads)
        self.assertIn("rtdl_optix_prepare_fixed_radius_query_points_3d", api)
        self.assertIn("rtdl_optix_aggregate_prepared_query_ranked_fixed_radius_neighbor_summaries_3d_f32", api)
        self.assertIn("rtdl_optix_destroy_prepared_fixed_radius_query_points_3d", api)
        self.assertIn("rtdl_optix_prepare_fixed_radius_query_points_3d", prelude)
        self.assertIn("rtdl_optix_aggregate_prepared_query_ranked_fixed_radius_neighbor_summaries_3d_f32", prelude)
        self.assertNotIn("rtnn_prepared", workloads.lower())

    def test_python_runtime_and_runner_use_prepared_query_mode(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")
        runner = RUNNER.read_text(encoding="utf-8")
        harness = HARNESS.read_text(encoding="utf-8")

        self.assertIn("class PreparedOptixFixedRadiusQueryPoints3D", runtime)
        self.assertIn("def prepare_optix_fixed_radius_query_points_3d", runtime)
        self.assertIn("def aggregate_ranked_summary_prepared_queries", runtime)
        self.assertIn("prepared_query_uniform_cell_ranked_summary_aggregate_f32_direct", runtime)
        self.assertIn("PreparedOptixFixedRadiusQueryPoints3D", init)
        self.assertIn("prepare_optix_fixed_radius_query_points_3d", init)
        self.assertIn("ranked-summary-aggregate-prepared-query-float32", runner)
        self.assertIn("prepared.prepare_query_points", runner)
        self.assertIn("aggregate_ranked_summary_prepared_queries", runner)
        self.assertIn("device_resident_query_points", runner)
        self.assertIn("ranked-summary-aggregate-prepared-query-float32", harness)
        self.assertIn("prepared_query_aggregate_float32_median", harness)


if __name__ == "__main__":
    unittest.main()
