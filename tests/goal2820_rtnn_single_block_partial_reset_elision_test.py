from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs" / "reports" / "goal2820_rtnn_single_block_partial_reset_elision_2026-05-31.md"


class Goal2820RtnnSingleBlockPartialResetElisionTest(unittest.TestCase):
    def test_single_block_partial_path_returns_before_workspace_reset(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        start = workloads.index("aggregate_prepared_query_ranked_fixed_radius_neighbor_summaries_grid_3d_optix")
        end = workloads.index(
            "static void aggregate_prepared_query_ranked_fixed_radius_neighbor_summaries_grid_3d_batch_optix",
            start,
        )
        body = workloads[start:end]

        block_branch = body.index("if (use_block_partial_direct)")
        block_return = body.index("return aggregate;", block_branch)
        workspace_reset = body.index("cuMemsetD8(d_aggregate")
        workspace_lookup = body.index("prepared->d_ranked_aggregate->ptr")

        self.assertLess(block_branch, block_return)
        self.assertLess(block_return, workspace_lookup)
        self.assertLess(workspace_lookup, workspace_reset)
        self.assertIn("g_frn3d_grid_ranked_summary_aggregate_f32_blocks", body[:workspace_lookup])
        self.assertNotIn("rtnn", body.lower())

    def test_report_keeps_boundary_until_pod_measurement(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("implementation-pending-pod-evidence", report)
        self.assertIn("downloads per-block partials from the prepared-query", report)
        self.assertIn("Direct and two-step aggregate paths still reset", report)
        self.assertIn("No single-request performance conclusion is authorized", report)
        self.assertIn("No RTDL-beats-RTNN-paper claim is authorized", report)


if __name__ == "__main__":
    unittest.main()
