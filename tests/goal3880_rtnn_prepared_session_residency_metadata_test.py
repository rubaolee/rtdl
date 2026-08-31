from __future__ import annotations

from pathlib import Path
import json
import unittest
from unittest import mock

from examples.current.research_benchmarks.rtnn import rtdl_rtnn_benchmark_app as rtnn


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3880_rtnn_prepared_session_residency_metadata_2026-06-08.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal3880_rtnn_prepared_session_residency_a5000" / "summary.json"


class Goal3880RtnnPreparedSessionResidencyMetadataTest(unittest.TestCase):
    def test_prepared_optix_payload_exposes_explicit_residency_metadata(self) -> None:
        fake_runner_payload = {
            "ok": True,
            "query_count": 16,
            "search_count": 16,
            "result_mode": "ranked-summary-aggregate-prepared-query-batch-float32",
        }
        with mock.patch(
            "scripts.goal2348_rtnn_v2_2_external_runner.generate_point_file",
            return_value={"point_count": 16, "dimension": 3},
        ), mock.patch(
            "scripts.goal2348_rtnn_v2_2_external_runner.run_rtdl_batched_3d_neighbors",
            return_value=fake_runner_payload,
        ):
            payload = rtnn.rtnn_prepared_optix_ranked_summary_payload(
                point_count=16,
                radius=0.02,
                k=8,
                repeat=2,
                query_batch_size=16,
                distribution="uniform",
                seed=123,
            )

        self.assertEqual(payload["mode"], "prepared_optix_ranked_summary")
        self.assertEqual(payload["runner_payload"], fake_runner_payload)
        metadata = payload["prepared_session_residency"]
        self.assertEqual(metadata["explicit_reuse_helper"], "get_or_prepare_explicit_session")
        self.assertFalse(metadata["cache_enabled_by_default"])
        self.assertTrue(metadata["cold_hot_phase_split_required"])
        self.assertTrue(metadata["prepare_once_query_many_pattern"])
        self.assertFalse(metadata["automatic_partner_selection_authorized"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])

        cache_key = metadata["cache_key"]
        self.assertEqual(cache_key["primitive"], "fixed_radius_neighbors_3d_ranked_summary")
        self.assertEqual(cache_key["backend"], "optix")
        self.assertEqual(cache_key["partner"], "none")
        self.assertEqual(cache_key["device"], "cuda:0")
        self.assertTrue(cache_key["explicit_key_required"])

        policy = metadata["policy"]
        self.assertEqual(policy["lifetime_state"], "session_retained")
        self.assertIn("explicit_invalidate", policy["invalidation_events"])
        self.assertFalse(policy["automatic_partner_selection_authorized"])
        self.assertFalse(policy["true_zero_copy_claim_authorized"])

        self.assertFalse(payload["claim_boundary"]["automatic_partner_selection_authorized"])
        self.assertFalse(payload["claim_boundary"]["true_zero_copy_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["native_engine_customization"])

    def test_report_documents_non_hidden_app_integration(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3880",
            "prepared_session_residency",
            "get_or_prepare_explicit_session",
            "cache_enabled_by_default = false",
            "not a hidden cache",
            "fixed_radius_neighbors_3d_ranked_summary",
            "A5000 Evidence",
        ):
            self.assertIn(phrase, text)

    def test_a5000_artifact_confirms_live_payload_metadata(self) -> None:
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        self.assertTrue(payload["all_pass"])
        self.assertEqual(payload["selected_prepared_session_residency_profile_count"], 1)
        self.assertEqual(len(payload["rows"]), 1)
        row = payload["rows"][0]
        self.assertEqual(row["row_id"], "rtnn_prepared_optix_scale_default_65536")
        self.assertTrue(row["prepared_session_residency_profiled"])

        stdout_path = POD_ARTIFACT.parent / "outputs" / "rtnn_prepared_optix_scale_default_65536.stdout.json"
        app_payload = json.loads(stdout_path.read_text(encoding="utf-8"))
        metadata = app_payload["prepared_session_residency"]
        self.assertEqual(metadata["explicit_reuse_helper"], "get_or_prepare_explicit_session")
        self.assertFalse(metadata["cache_enabled_by_default"])
        self.assertEqual(metadata["cache_key"]["primitive"], "fixed_radius_neighbors_3d_ranked_summary")
        self.assertFalse(app_payload["claim_boundary"]["automatic_partner_selection_authorized"])
        self.assertFalse(app_payload["claim_boundary"]["true_zero_copy_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
