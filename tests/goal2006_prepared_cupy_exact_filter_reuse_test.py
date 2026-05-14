from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "src" / "rtdsl" / "partner_adapters.py"
PERF_SCRIPT = ROOT / "scripts" / "goal1869_road_hazard_v2_partner_perf.py"
SMOKE_SCRIPT = ROOT / "scripts" / "goal1868_road_hazard_partner_priority_flags_pod_smoke.py"
REPORT = ROOT / "docs" / "reports" / "goal2006_prepared_cupy_exact_filter_reuse_2026-05-14.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2006_pod_smoke" / "road_hazard_prepared_cupy_exact_filter_2048.json"
CLAUDE_REVIEW = ROOT / "docs" / "reviews" / "goal2007_claude_review_goal2006_prepared_cupy_exact_filter_2026-05-14.md"
GEMINI_REVIEW = ROOT / "docs" / "reviews" / "goal2008_gemini_review_goal2006_prepared_cupy_exact_filter_2026-05-14.md"


class Goal2006PreparedCupyExactFilterReuseTest(unittest.TestCase):
    def test_prepared_scene_retains_partner_triangle_columns_for_exact_filter(self) -> None:
        text = ADAPTER.read_text(encoding="utf-8")

        self.assertIn("class _PartnerPreparedTriangleScene", text)
        self.assertIn("self.polygon_triangle_columns = polygon_triangle_columns", text)
        self.assertIn("_cupy_exact_filter_triangle_lookup_cache", text)
        self.assertIn("triangle_lookup_cache[\"sorted_triangle_ids\"]", text)
        self.assertIn("prepared_triangle_columns = getattr(prepared_scene, \"polygon_triangle_columns\", None)", text)
        self.assertIn("_cupy_exact_segment_triangle_witness_pairs(", text)
        self.assertIn("partner_gpu_unique_pair_counts_from_prepared_cupy_exact_filter", text)
        self.assertIn('"app_exact_filter": "not_available_for_prepared_scene_without_partner_triangle_columns"', text)
        self.assertIn('"native_engine_row_contract": "generic_ray_primitive_candidate_witness_pairs"', text)
        self.assertIn('"whole_app_true_zero_copy_authorized": whole_app_true_zero_copy_authorized', text)

    def test_road_hazard_scripts_use_float32_ray_columns_for_optix_device_abi(self) -> None:
        for path in (PERF_SCRIPT, SMOKE_SCRIPT):
            text = path.read_text(encoding="utf-8")
            for name in ("ox", "oy", "dx", "dy", "tmax"):
                self.assertIn(f'"{name}": runtime["tensor"]', text)
            self.assertIn('runtime["float32"]', text)

    def test_report_records_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: pod-pass-with-boundary", report)
        self.assertIn("generic_ray_primitive_candidate_witness_pairs", report)
        self.assertIn("CuPy RawKernel exact segment/triangle filter", report)
        self.assertIn("does not authorize", report)
        self.assertIn("v2.0 release readiness", report)
        self.assertIn("triangle-side sort is reusable", report)

    def test_pod_artifact_records_exact_prepared_cupy_parity_and_speed(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(artifact["status"], "pass")
        self.assertEqual(artifact["count"], 2048)
        self.assertIn("NVIDIA RTX A5000", artifact["gpu"])
        self.assertTrue(artifact["parity"]["strict_priority_flags_match"])
        prepared = artifact["partners"]["cupy"]["goal1889_prepared_reuse"]
        self.assertTrue(prepared["prepared_scene_reused"])
        self.assertTrue(prepared["witness_output_columns_reused"])
        self.assertEqual(
            prepared["metadata"]["app_count_materialization"],
            "partner_gpu_unique_pair_counts_from_prepared_cupy_exact_filter",
        )
        self.assertEqual(
            prepared["metadata"]["app_exact_filter"],
            "cupy_rawkernel_segment_triangle_filter_from_generic_witness_candidates",
        )
        self.assertTrue(prepared["metadata"]["whole_app_true_zero_copy_authorized"])
        self.assertLess(prepared["query_median_ratio_vs_v1_8_prepared_native"], 1.0)
        self.assertLess(prepared["query_median_ratio_vs_goal1869_unprepared_partner"], 1.0)
        boundary = artifact["claim_boundary"]
        self.assertTrue(boundary["partner_output_columns_true_zero_copy_authorized"])
        self.assertFalse(boundary["v2_0_release_authorized"])
        self.assertFalse(boundary["whole_app_speedup_claim_authorized"])
        self.assertFalse(boundary["broad_rt_core_speedup_claim_authorized"])

    def test_external_reviews_exist_with_bounded_verdicts(self) -> None:
        claude = CLAUDE_REVIEW.read_text(encoding="utf-8")
        gemini = GEMINI_REVIEW.read_text(encoding="utf-8")

        self.assertIn("Verdict: **accept-with-boundary**", claude)
        self.assertIn("candidate-only", claude)
        self.assertIn("Verdict: accept", gemini)
        self.assertIn("does not overclaim", gemini)


if __name__ == "__main__":
    unittest.main()
