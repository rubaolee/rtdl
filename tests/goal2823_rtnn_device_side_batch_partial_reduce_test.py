from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs" / "reports" / "goal2823_rtnn_device_side_batch_partial_reduce_2026-05-31.md"


class Goal2823RtnnDeviceSideBatchPartialReduceTest(unittest.TestCase):
    def test_core_adds_generic_device_side_partial_reducer(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        start = core.index("fixed_radius_neighbors_3d_ranked_aggregate_partials_reduce")
        end = core.index("extern \"C\" __global__ void fixed_radius_neighbors_3d_grid_compact", start)
        kernel = core[start:end]

        self.assertIn("const FrnRankedAggregate* partials", kernel)
        self.assertIn("uint32_t partial_count", kernel)
        self.assertIn("uint32_t request_count", kernel)
        self.assertIn("const uint32_t request_index = blockIdx.x", kernel)
        self.assertIn("const uint32_t base = request_index * partial_count", kernel)
        self.assertIn("aggregates_out[request_index].query_count", kernel)
        self.assertNotIn("rtnn", kernel.lower())

    def test_batch_path_reduces_partials_on_device_before_compact_download(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        start = workloads.index("aggregate_prepared_query_ranked_fixed_radius_neighbor_summaries_grid_3d_batch_optix")
        end = workloads.index("static void run_prepared_fixed_radius_neighbors_grid_3d_optix", start)
        body = workloads[start:end]

        self.assertIn("g_frn3d_ranked_aggregate_partials_reduce", workloads)
        self.assertIn("DevPtr d_aggregates(sizeof(RtdlFixedRadiusRankedNeighborAggregate) * request_count)", body)
        self.assertIn("cuLaunchKernel(g_frn3d_ranked_aggregate_partials_reduce.fn", body)
        self.assertIn("&partial_count_u32", body)
        self.assertIn("download(aggregates_out, d_aggregates.ptr, request_count)", body)
        self.assertNotIn("std::vector<RtdlFixedRadiusRankedNeighborAggregate> partials(request_count * grid)", body)
        self.assertNotIn("partials[request_index * grid + partial_index]", body)
        self.assertNotIn("rtnn", body.lower())

    def test_report_keeps_boundary_until_pod_evidence(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("implementation-pending-pod-evidence", report)
        self.assertIn("device-side final reduction kernel", report)
        self.assertIn("downloads only one aggregate row per request", report)
        self.assertIn("No performance conclusion is authorized", report)


if __name__ == "__main__":
    unittest.main()
