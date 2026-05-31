from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"


class Goal2815RtnnPreparedAggregateWorkspaceTest(unittest.TestCase):
    def test_prepared_fixed_radius_handle_owns_reusable_aggregate_workspace(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("std::unique_ptr<DevPtr> d_ranked_aggregate", workloads)
        self.assertIn(
            "d_ranked_aggregate = std::make_unique<DevPtr>(sizeof(RtdlFixedRadiusRankedNeighborAggregate))",
            workloads,
        )

        start = workloads.index("aggregate_prepared_query_ranked_fixed_radius_neighbor_summaries_grid_3d_optix")
        end = workloads.index("static void run_prepared_fixed_radius_neighbors_grid_3d_optix", start)
        prepared_query_body = workloads[start:end]

        self.assertIn("prepared->d_ranked_aggregate->ptr", prepared_query_body)
        self.assertIn("CUdeviceptr d_aggregate", prepared_query_body)
        self.assertIn("cuMemsetD8(d_aggregate", prepared_query_body)
        self.assertNotIn("DevPtr d_aggregate", prepared_query_body)
        self.assertNotIn("rtnn", prepared_query_body.lower())

    def test_non_resident_query_aggregate_path_uses_same_workspace(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")

        start = workloads.index("aggregate_prepared_ranked_fixed_radius_neighbor_summaries_grid_3d_optix")
        end = workloads.index("aggregate_prepared_query_ranked_fixed_radius_neighbor_summaries_grid_3d_optix", start)
        aggregate_body = workloads[start:end]

        self.assertIn("prepared->d_ranked_aggregate->ptr", aggregate_body)
        self.assertIn("CUdeviceptr d_aggregate", aggregate_body)
        self.assertIn("cuMemsetD8(d_aggregate", aggregate_body)
        self.assertNotIn("DevPtr d_aggregate", aggregate_body)
        self.assertNotIn("rtnn", aggregate_body.lower())


if __name__ == "__main__":
    unittest.main()
