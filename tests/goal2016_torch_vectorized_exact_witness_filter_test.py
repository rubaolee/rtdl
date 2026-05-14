from __future__ import annotations

import pathlib
import json
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "src" / "rtdsl" / "partner_adapters.py"
REPORT = ROOT / "docs" / "reports" / "goal2016_torch_vectorized_exact_witness_filter_2026-05-14.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2016_pod_smoke" / "road_hazard_prepared_torch_exact_filter_2048.json"
ARTIFACT_4096 = ROOT / "docs" / "reports" / "goal2016_pod_smoke" / "road_hazard_prepared_torch_exact_filter_4096.json"
CLAUDE_REVIEW = ROOT / "docs" / "reviews" / "goal2017_claude_review_goal2016_torch_exact_filter_2026-05-14.md"
CLAUDE_ADDENDUM = ROOT / "docs" / "reviews" / "goal2019_claude_addendum_review_goal2016_torch_4096_2026-05-14.md"


class Goal2016TorchVectorizedExactWitnessFilterTest(unittest.TestCase):
    def test_torch_exact_filter_is_present_and_device_materialized(self) -> None:
        text = ADAPTER.read_text(encoding="utf-8")

        self.assertIn("def _torch_exact_segment_triangle_witness_pairs", text)
        self.assertIn("torch_vectorized_segment_triangle_filter_from_generic_witness_candidates", text)
        self.assertIn("partner_gpu_unique_pair_counts_from_torch_exact_filter", text)
        self.assertIn("partner_gpu_unique_pair_counts_from_prepared_torch_exact_filter", text)
        self.assertIn("_partner_exact_filter_triangle_lookup_cache", text)
        self.assertIn("candidate_ray_ids = runtime[\"slice\"](witness_ray_ids, emitted_count).to(torch.int64)", text)
        self.assertIn("native_engine_row_contract", text)

    def test_report_keeps_pod_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: pod-pass-with-boundary", text)
        self.assertIn("Torch/CuPy asymmetry", text)
        self.assertIn("generic_ray_primitive_candidate_witness_pairs", text)
        self.assertIn("0.005289506", text)
        self.assertIn("0.004532680", text)
        self.assertIn("1.76x", text)
        self.assertIn("goal2019_claude_addendum_review_goal2016_torch_4096", text)
        self.assertIn("accept-with-boundary", text)

    def test_pod_artifact_records_torch_device_exact_filter_and_boundary(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(artifact["status"], "pass")
        self.assertEqual(artifact["count"], 2048)
        self.assertTrue(artifact["parity"]["strict_priority_flags_match"])
        row = artifact["partners"]["torch"]["goal1889_prepared_reuse"]
        self.assertEqual(
            row["metadata"]["app_exact_filter"],
            "torch_vectorized_segment_triangle_filter_from_generic_witness_candidates",
        )
        self.assertEqual(
            row["metadata"]["app_count_materialization"],
            "partner_gpu_unique_pair_counts_from_prepared_torch_exact_filter",
        )
        self.assertTrue(row["metadata"]["whole_app_true_zero_copy_authorized"])
        self.assertGreater(row["query_median_ratio_vs_v1_8_prepared_native"], 1.0)
        self.assertFalse(artifact["claim_boundary"]["v2_0_release_authorized"])

    def test_larger_pod_artifact_records_scale_sensitive_torch_speedup(self) -> None:
        artifact = json.loads(ARTIFACT_4096.read_text(encoding="utf-8"))

        self.assertEqual(artifact["status"], "pass")
        self.assertEqual(artifact["count"], 4096)
        self.assertTrue(artifact["parity"]["strict_priority_flags_match"])
        row = artifact["partners"]["torch"]["goal1889_prepared_reuse"]
        self.assertLess(row["query_median_ratio_vs_v1_8_prepared_native"], 0.6)
        self.assertEqual(
            row["metadata"]["app_exact_filter"],
            "torch_vectorized_segment_triangle_filter_from_generic_witness_candidates",
        )
        self.assertTrue(row["metadata"]["whole_app_true_zero_copy_authorized"])

    def test_claude_review_accepts_with_boundary(self) -> None:
        review = CLAUDE_REVIEW.read_text(encoding="utf-8")

        self.assertIn("Verdict: **accept-with-boundary**", review)
        self.assertIn("Native OptiX remains app-agnostic and candidate-only", review)
        self.assertIn("Implementation risks", review)

    def test_claude_addendum_accepts_scale_sensitive_boundary(self) -> None:
        review = CLAUDE_ADDENDUM.read_text(encoding="utf-8")

        self.assertIn("Verdict: **accept-with-boundary**", review)
        self.assertIn("Distinguishes 2048 negative from 4096 positive evidence", review)
        self.assertIn("Avoids broad claims", review)


if __name__ == "__main__":
    unittest.main()
