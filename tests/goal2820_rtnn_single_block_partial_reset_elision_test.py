from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs" / "reports" / "goal2820_rtnn_single_block_partial_reset_elision_2026-05-31.md"
POD_ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2820_rtnn_single_block_partial_reset_elision_pod"
POD_SUMMARY = POD_ARTIFACT_DIR / "goal2820_summary.json"


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

    def test_report_records_neutral_pod_measurement(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("neutral single-request performance evidence", report)
        self.assertIn("downloads per-block partials from the prepared-query", report)
        self.assertIn("Direct and two-step aggregate paths still reset", report)
        self.assertIn("correct but not a material single-request speedup", report)
        self.assertIn("uniform 32K", report)
        self.assertIn("uniform 65K", report)
        self.assertIn("No RTDL-beats-RTNN-paper claim is authorized", report)

    def test_pod_artifacts_are_clean_and_bounded(self) -> None:
        summary = json.loads(POD_SUMMARY.read_text(encoding="utf-8"))

        self.assertEqual(summary["status"], "pass")
        self.assertEqual(summary["source_commit"], "827b076644146d29c4aac8b8f36c0945f59b74ba")
        self.assertEqual(summary["source_dirty"], [])
        self.assertEqual([row["point_count"] for row in summary["rows"]], [32768, 65536])

        changes = {row["point_count"]: row["change_vs_goal2819"] for row in summary["rows"]}
        self.assertLess(changes[32768], 1.0)
        self.assertGreater(changes[65536], 1.0)

        for row in summary["rows"]:
            self.assertEqual(row["status"], "pass")
            self.assertEqual(row["source_dirty"], [])
            self.assertEqual(
                row["phase_summary"][0]["mode"],
                "prepared_query_uniform_cell_ranked_summary_aggregate_f32_block_partials",
            )
            self.assertFalse(row["claim_boundary"]["public_speedup_claim_authorized"])
            self.assertFalse(row["claim_boundary"]["rtdl_beats_rtnn_claim_authorized"])
            self.assertTrue(row["claim_boundary"]["single_request_internal_delta_only"])


if __name__ == "__main__":
    unittest.main()
