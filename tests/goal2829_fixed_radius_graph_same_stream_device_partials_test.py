import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
OPTIX_API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
OPTIX_WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
OPTIX_PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
REPORT = ROOT / "docs" / "reports" / "goal2829_fixed_radius_graph_same_stream_device_partials_2026-05-31.md"
POD_SUMMARY = (
    ROOT
    / "docs"
    / "reports"
    / "goal2829_fixed_radius_graph_same_stream_device_partials_pod"
    / "goal2829_summary.json"
)
REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "goal2830_gemini_review_goal2829_fixed_radius_graph_same_stream_partials_2026-05-31.md"
)
CONSENSUS = ROOT / "docs" / "reports" / "goal2830_goal2829_same_stream_partials_consensus_2026-05-31.md"


class Goal2829FixedRadiusGraphSameStreamDevicePartialsTest(unittest.TestCase):
    def test_native_exports_explicit_unsynchronized_device_partial_launch(self):
        api = OPTIX_API.read_text(encoding="utf-8")
        prelude = OPTIX_PRELUDE.read_text(encoding="utf-8")
        workloads = OPTIX_WORKLOADS.read_text(encoding="utf-8")
        symbol = (
            "rtdl_optix_launch_fixed_radius_ranked_summary_aggregate_batch_graph_"
            "device_partials_3d"
        )
        self.assertIn(symbol, api)
        self.assertIn(symbol, prelude)
        self.assertIn(
            "launch_fixed_radius_ranked_summary_aggregate_batch_graph_device_partials_3d_optix",
            workloads,
        )

        match = re.search(
            r"static void launch_fixed_radius_ranked_summary_aggregate_batch_graph_device_partials_3d_optix"
            r"\([\s\S]+?\n}\n\nstatic void run_prepared_fixed_radius_neighbors_grid_3d_optix",
            workloads,
        )
        self.assertIsNotNone(match)
        launch_body = match.group(0)
        self.assertIn("cuGraphLaunch(graph_handle->graph_exec, graph_handle->stream)", launch_body)
        self.assertIn("graph_handle->d_partials->ptr", launch_body)
        self.assertIn("reinterpret_cast<uint64_t>(graph_handle->stream)", launch_body)
        self.assertNotIn("cuStreamSynchronize", launch_body)
        self.assertNotIn("download(", launch_body)

    def test_python_api_exposes_bounded_same_stream_cupy_consumer(self):
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        self.assertIn("def replay_same_stream_device_partials_summary_cupy", runtime)
        self.assertIn("_run_fixed_radius_graph_partials_same_stream_summary_cupy", runtime)
        self.assertIn("cp.cuda.ExternalStream(int(cuda_stream_ptr))", runtime)
        self.assertIn("cp.cuda.UnownedMemory", runtime)
        self.assertIn("host_scalar_read_before_consumer", runtime)
        self.assertIn("host_partial_materialization_before_consumer", runtime)
        self.assertIn("producer_host_synchronization_used", runtime)
        self.assertIn(
            "bounded_same_stream_fixed_radius_graph_partial_summary_consumer_only",
            runtime,
        )

    def test_claim_boundaries_remain_explicit(self):
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("does not authorize broad true-zero-copy", text)
        self.assertIn("public_speedup_claim_authorized: false", text)
        self.assertIn('"true_zero_copy_authorized": False', runtime)
        self.assertIn('"public_speedup_claim_authorized": False', runtime)
        self.assertIn('"general_partner_continuation_authorized": False', runtime)

    def test_pod_review_and_consensus_evidence_exist(self):
        summary = POD_SUMMARY.read_text(encoding="utf-8")
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn('"ok": true', summary)
        self.assertIn('"producer_consumer_stream_ordering": "same_cuda_stream"', summary)
        self.assertIn('"host_scalar_read_before_consumer": false', summary)
        self.assertIn('"host_partial_materialization_before_consumer": false', summary)

        self.assertIn("`accept-with-boundary`", review)
        self.assertIn("no calls to `cuStreamSynchronize`", review)
        self.assertIn("cupy.cuda.ExternalStream", review)
        self.assertIn("cupy.cuda.UnownedMemory", review)

        self.assertIn("Codex + Gemini consensus accepts Goal2829 with boundary", consensus)
        self.assertIn("Broad public performance/release claims | not authorized", consensus)
        self.assertIn("partner-neutral typed primitive-payload column descriptor", consensus)


if __name__ == "__main__":
    unittest.main()
