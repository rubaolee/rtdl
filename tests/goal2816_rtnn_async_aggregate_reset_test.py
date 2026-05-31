from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"


class Goal2816RtnnAsyncAggregateResetTest(unittest.TestCase):
    def test_prepared_aggregate_reset_is_enqueued_on_default_stream(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("cuMemsetD8Async(d_aggregate", workloads)
        self.assertNotIn("cuMemsetD8(d_aggregate", workloads)
        self.assertIn("cuLaunchKernel(g_frn3d_grid_ranked_summary_aggregate_f32_direct.fn", workloads)

    def test_reset_change_does_not_introduce_app_specific_terms(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        start = workloads.index("aggregate_prepared_query_ranked_fixed_radius_neighbor_summaries_grid_3d_optix")
        end = workloads.index("static void run_prepared_fixed_radius_neighbors_grid_3d_optix", start)
        body = workloads[start:end]

        self.assertIn("cuMemsetD8Async", body)
        self.assertNotIn("rtnn", body.lower())


if __name__ == "__main__":
    unittest.main()
