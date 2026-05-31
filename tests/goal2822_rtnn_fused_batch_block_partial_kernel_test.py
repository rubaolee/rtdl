from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs" / "reports" / "goal2822_rtnn_fused_batch_block_partial_kernel_2026-05-31.md"
POD_ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2822_rtnn_fused_batch_block_partial_kernel_pod"
POD_SUMMARY = POD_ARTIFACT_DIR / "goal2822_summary.json"


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
        self.assertNotIn("cuLaunchKernel(g_frn3d_grid_ranked_summary_aggregate_f32_blocks.fn", body)
        self.assertNotIn("rtnn", body.lower())

    def test_report_keeps_boundary_until_pod_evidence(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("accept-with-boundary", report)
        self.assertIn("fused 2D-grid block-partial kernel", report)
        self.assertIn("1.105x", report)
        self.assertIn("1.085x", report)
        self.assertIn("modestly faster than Goal2821", report)
        self.assertIn("No RTDL-beats-RTNN-paper claim is authorized", report)

    def test_pod_artifacts_record_clean_fused_batch_evidence(self) -> None:
        summary = json.loads(POD_SUMMARY.read_text(encoding="utf-8"))

        self.assertEqual(summary["status"], "pass")
        self.assertEqual(summary["source_commit"], "ef2204808d9997729b194d743f76a8508fd84a85")
        self.assertEqual(summary["source_dirty"], [])
        self.assertEqual([row["point_count"] for row in summary["rows"]], [32768, 65536])

        by_count = {row["point_count"]: row for row in summary["rows"]}
        self.assertGreater(by_count[32768]["change_vs_goal2821_batch"], 1.08)
        self.assertGreater(by_count[65536]["change_vs_goal2821_batch"], 1.05)
        self.assertGreater(by_count[32768]["amortized_improvement_vs_sequential"], 1.2)
        self.assertGreater(by_count[65536]["amortized_improvement_vs_sequential"], 2.0)

        for row in summary["rows"]:
            self.assertEqual(row["status"], "pass")
            self.assertEqual(row["source_dirty"], [])
            self.assertTrue(row["batch_results_match_sequential"])
            self.assertEqual(
                row["phase_summary_after_batch"]["mode"],
                "prepared_query_uniform_cell_ranked_summary_aggregate_f32_batch_block_partials",
            )
            self.assertFalse(row["claim_boundary"]["public_speedup_claim_authorized"])
            self.assertFalse(row["claim_boundary"]["single_request_speedup_claim_authorized"])
            self.assertTrue(row["claim_boundary"]["fused_batch_internal_evidence_only"])


if __name__ == "__main__":
    unittest.main()
