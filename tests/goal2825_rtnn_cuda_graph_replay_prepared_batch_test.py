from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
RUNNER = ROOT / "scripts" / "goal2348_rtnn_v2_2_external_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal2825_rtnn_cuda_graph_replay_prepared_batch_2026-05-31.md"
REVIEW = ROOT / "docs" / "reviews" / "goal2826_gemini_review_goal2825_cuda_graph_replay_2026-05-31.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal2826_goal2825_cuda_graph_replay_consensus_2026-05-31.md"
POD_ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2825_rtnn_cuda_graph_replay_pod"
POD_SUMMARY = POD_ARTIFACT_DIR / "goal2825_summary.json"


class Goal2825RtnnCudaGraphReplayPreparedBatchTest(unittest.TestCase):
    def test_native_backend_adds_generic_static_cuda_graph_handle(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")

        self.assertIn("struct PreparedFixedRadiusRankedSummaryAggregateBatchGraph3D", workloads)
        self.assertIn("CUgraph graph = nullptr", workloads)
        self.assertIn("CUgraphExec graph_exec = nullptr", workloads)
        self.assertIn("cuStreamBeginCapture(stream, CU_STREAM_CAPTURE_MODE_GLOBAL)", workloads)
        self.assertIn("g_frn3d_grid_ranked_summary_aggregate_f32_blocks_batch.fn", workloads)
        self.assertIn("cuGraphLaunch(graph_handle->graph_exec, graph_handle->stream)", workloads)
        self.assertIn("reset_fixed_radius_3d_phase_timings(18u)", workloads)
        self.assertIn("graph path currently supports query_count <= 65536", workloads)
        self.assertNotIn("rtnn", workloads.lower())

        self.assertIn("rtdl_optix_prepare_fixed_radius_ranked_summary_aggregate_batch_graph_3d", api)
        self.assertIn("rtdl_optix_replay_fixed_radius_ranked_summary_aggregate_batch_graph_3d", api)
        self.assertIn("rtdl_optix_destroy_fixed_radius_ranked_summary_aggregate_batch_graph_3d", api)

    def test_python_runtime_exposes_explicit_opt_in_graph_replay(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")
        runner = RUNNER.read_text(encoding="utf-8")

        self.assertIn("class PreparedOptixFixedRadiusRankedSummaryAggregateBatchGraph3D", runtime)
        self.assertIn("prepare_ranked_summary_prepared_queries_batch_graph", runtime)
        self.assertIn("rtdl_optix_prepare_fixed_radius_ranked_summary_aggregate_batch_graph_3d", runtime)
        self.assertIn("rtdl_optix_replay_fixed_radius_ranked_summary_aggregate_batch_graph_3d", runtime)
        self.assertIn(
            "prepared_query_uniform_cell_ranked_summary_aggregate_f32_batch_cuda_graph_replay",
            runtime,
        )
        self.assertIn("cuda_graph_replay", runtime)
        self.assertIn("PreparedOptixFixedRadiusRankedSummaryAggregateBatchGraph3D", init)

        mode = "ranked-summary-aggregate-prepared-query-batch-graph-float32"
        self.assertIn(mode, runner)
        self.assertIn("prepared_cuda_graph_replay", runner)
        self.assertIn("prepare_ranked_summary_prepared_queries_batch_graph", runner)

    def test_report_records_narrow_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("accept-with-boundary", report)
        self.assertIn("CUDA graph replay", report)
        self.assertIn("opt-in", report)
        self.assertIn("1.156x", report)
        self.assertIn("1.026x", report)
        self.assertIn("public RTDL-beats-CuPy wording", report)
        self.assertIn("does not change the default runtime path", report)

    def test_gemini_review_and_consensus_accept_with_boundary(self) -> None:
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Verdict: `accept-with-boundary`", review)
        self.assertIn("native engine remains app-agnostic", review)
        self.assertIn("explicit opt-in", review)
        self.assertIn("1.156x and 1.026x", review)
        self.assertIn("claim boundary is strictly maintained", review)

        self.assertIn("Codex + Gemini consensus accepts Goal2825 with boundary", consensus)
        self.assertIn("Default runtime change | not authorized", consensus)
        self.assertIn("v2.5 release wording", consensus)
        self.assertIn("same_ranked_aggregate_batch_summaries_normalized", consensus)

    def test_pod_artifacts_record_graph_replay_evidence(self) -> None:
        summary = json.loads(POD_SUMMARY.read_text(encoding="utf-8"))

        self.assertEqual(summary["goal"], "Goal2825")
        self.assertIn("NVIDIA RTX A5000", summary["gpu"])
        self.assertEqual(
            summary["source_commit_before_patch"],
            "c542ba8006458ac9784f89418c794e72399e1b45",
        )
        self.assertEqual([row["point_count"] for row in summary["rows"]], [32768, 65536])

        by_count = {row["point_count"]: row for row in summary["rows"]}
        self.assertGreater(by_count[32768]["graph_replay_vs_fused_batch"], 1.10)
        self.assertGreater(by_count[65536]["graph_replay_vs_fused_batch"], 1.00)
        self.assertGreater(summary["speedup_graph_replay_vs_fused_normalized_max"], 1.10)
        self.assertGreater(summary["speedup_graph_replay_vs_fused_normalized_min"], 1.00)

        for row in summary["rows"]:
            self.assertTrue(row["same_ranked_aggregate_summary"])
            self.assertTrue(row["same_ranked_aggregate_batch_summaries_normalized"])
            self.assertEqual(
                row["fused_phase_mode"],
                "prepared_query_uniform_cell_ranked_summary_aggregate_f32_batch_block_partials",
            )
            self.assertEqual(
                row["graph_phase_mode"],
                "prepared_query_uniform_cell_ranked_summary_aggregate_f32_batch_cuda_graph_replay",
            )

        boundary = summary["claim_boundary"]
        self.assertTrue(boundary["prepared_static_cuda_graph_replay_probe"])
        self.assertFalse(boundary["default_runtime_changed"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])
        self.assertFalse(boundary["rtnn_paper_reproduction_claim_authorized"])
        self.assertFalse(boundary["whole_app_speedup_claim_authorized"])
        self.assertFalse(boundary["v2_5_release_authorized"])


if __name__ == "__main__":
    unittest.main()
