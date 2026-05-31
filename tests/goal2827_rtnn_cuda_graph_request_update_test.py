from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
REPORT = ROOT / "docs" / "reports" / "goal2827_rtnn_cuda_graph_request_update_2026-05-31.md"
REVIEW = ROOT / "docs" / "reviews" / "goal2828_gemini_review_goal2827_cuda_graph_request_update_2026-05-31.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal2828_goal2827_cuda_graph_request_update_consensus_2026-05-31.md"
POD_SUMMARY = ROOT / "docs" / "reports" / "goal2827_rtnn_cuda_graph_request_update_pod" / "goal2827_summary.json"


class Goal2827RtnnCudaGraphRequestUpdateTest(unittest.TestCase):
    def test_native_graph_handle_updates_request_buffers_without_app_terms(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")

        self.assertIn("void update_requests(", workloads)
        self.assertIn("graph request update requires unchanged request_count", workloads)
        self.assertIn("upload(d_radii->ptr, radii_f.data(), request_count)", workloads)
        self.assertIn("upload(d_k_values->ptr, k_values_u32.data(), request_count)", workloads)
        self.assertIn("update_fixed_radius_ranked_summary_aggregate_batch_graph_3d_optix", workloads)
        self.assertNotIn("rtnn", workloads.lower())

        self.assertIn("rtdl_optix_update_fixed_radius_ranked_summary_aggregate_batch_graph_3d", api)
        self.assertIn("update_fixed_radius_ranked_summary_aggregate_batch_graph_3d_optix", api)

    def test_python_runtime_exposes_same_shape_request_update(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")

        self.assertIn("def update_requests(self, requests) -> None:", runtime)
        self.assertIn("_normalize_fixed_radius_graph_requests", runtime)
        self.assertIn("request updates must keep request_count unchanged", runtime)
        self.assertIn("request_buffer_update_count", runtime)
        self.assertIn("rtdl_optix_update_fixed_radius_ranked_summary_aggregate_batch_graph_3d", runtime)
        self.assertIn("ctypes.POINTER(ctypes.c_double)", runtime)
        self.assertIn("ctypes.POINTER(ctypes.c_size_t)", runtime)

    def test_report_keeps_boundary_and_next_step(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("accept-with-boundary", report)
        self.assertIn("same-shape `(radius, k_max)` sweep", report)
        self.assertIn("No RTNN-specific native ABI", report)
        self.assertIn("1.062x", report)
        self.assertIn("making graph replay the default path", report)
        self.assertIn("event-ordered chaining", report)

    def test_gemini_review_and_consensus_accept_with_boundary(self) -> None:
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("`accept-with-boundary`", review)
        self.assertIn("app-agnostic", review)
        self.assertIn("unchanged request count", review)
        self.assertIn("1.062x", review)
        self.assertIn("Any performance wording must be scoped exclusively to Goal2827", review)

        self.assertIn("Codex + Gemini consensus accepts Goal2827 with boundary", consensus)
        self.assertIn("Same-shape request-update constraint | accept", consensus)
        self.assertIn("Default runtime change | not authorized", consensus)
        self.assertIn("direct_b_matches_updated_graph_b", consensus)

    def test_pod_artifact_records_exact_parity_and_modest_update_win(self) -> None:
        summary = json.loads(POD_SUMMARY.read_text(encoding="utf-8"))

        self.assertEqual(summary["goal"], "Goal2827")
        self.assertEqual(summary["point_count"], 32768)
        self.assertEqual(summary["request_count"], 4)
        self.assertTrue(summary["same_shape_request_update"])
        self.assertTrue(summary["direct_a_matches_graph_a"])
        self.assertTrue(summary["direct_b_matches_updated_graph_b"])
        self.assertEqual(summary["request_buffer_update_count_after_b"], 1)
        self.assertGreater(summary["update_replay_vs_rebuild_replay"], 1.0)
        self.assertEqual(
            summary["phase_after_update"]["mode"],
            "prepared_query_uniform_cell_ranked_summary_aggregate_f32_batch_cuda_graph_replay",
        )

        boundary = summary["claim_boundary"]
        self.assertTrue(boundary["same_shape_graph_request_update_probe"])
        self.assertFalse(boundary["default_runtime_changed"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])
        self.assertFalse(boundary["rtnn_paper_reproduction_claim_authorized"])
        self.assertFalse(boundary["whole_app_speedup_claim_authorized"])
        self.assertFalse(boundary["v2_5_release_authorized"])


if __name__ == "__main__":
    unittest.main()
