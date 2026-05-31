from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs" / "reports" / "goal2822_rtnn_fused_batch_block_partial_kernel_2026-05-31.md"


class Goal2822RtnnFusedBatchBlockPartialKernelTest(unittest.TestCase):
    def test_core_adds_generic_two_dimensional_batch_kernel(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        start = core.index("fixed_radius_neighbors_3d_grid_ranked_summary_aggregate_f32_blocks_batch")
        end = core.index("extern \"C\" __global__ void fixed_radius_neighbors_3d_grid_compact", start)
        kernel = core[start:end]

        self.assertIn("const float* radii", kernel)
        self.assertIn("const uint32_t* k_values", kernel)
        self.assertIn("const uint32_t request_index = blockIdx.y", kernel)
        self.assertIn("const float radius = radii[request_index]", kernel)
        self.assertIn("const uint32_t k_max = k_values[request_index]", kernel)
        self.assertIn("const uint32_t output_index = request_index * gridDim.x + blockIdx.x", kernel)
        self.assertNotIn("rtnn", kernel.lower())

    def test_workloads_uses_single_fused_launch_for_block_partial_batch(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        start = workloads.index("aggregate_prepared_query_ranked_fixed_radius_neighbor_summaries_grid_3d_batch_optix")
        end = workloads.index("static void run_prepared_fixed_radius_neighbors_grid_3d_optix", start)
        body = workloads[start:end]

        self.assertIn("g_frn3d_grid_ranked_summary_aggregate_f32_blocks_batch", workloads)
        self.assertIn("std::vector<float> radii_f(request_count)", body)
        self.assertIn("std::vector<uint32_t> k_values_u32(request_count)", body)
        self.assertIn("upload(d_radii.ptr, radii_f.data(), request_count)", body)
        self.assertIn("upload(d_k_values.ptr, k_values_u32.data(), request_count)", body)
        self.assertIn("cuLaunchKernel(g_frn3d_grid_ranked_summary_aggregate_f32_blocks_batch.fn", body)
        self.assertIn("grid, request_count_u32, 1", body)
        self.assertIn("partials[request_index * grid + partial_index]", body)
        self.assertNotIn("cuLaunchKernel(g_frn3d_grid_ranked_summary_aggregate_f32_blocks.fn", body)
        self.assertNotIn("rtnn", body.lower())

    def test_report_keeps_boundary_until_pod_evidence(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("implementation-pending-pod-evidence", report)
        self.assertIn("fused 2D-grid block-partial kernel", report)
        self.assertIn("No performance conclusion is authorized", report)
        self.assertIn("No RTDL-beats-RTNN-paper claim is authorized", report)


if __name__ == "__main__":
    unittest.main()
