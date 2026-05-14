from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "src" / "rtdsl" / "partner_adapters.py"
REPORT = ROOT / "docs" / "reports" / "goal2009_prepared_cupy_triangle_lookup_cache_2026-05-14.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2009_pod_smoke" / "road_hazard_prepared_cupy_cached_triangle_lookup_2048.json"
ARTIFACT_4096 = ROOT / "docs" / "reports" / "goal2009_pod_smoke" / "road_hazard_prepared_cupy_cached_triangle_lookup_4096.json"
CLAUDE_REVIEW = ROOT / "docs" / "reviews" / "goal2010_claude_review_goal2009_prepared_cupy_triangle_lookup_cache_2026-05-14.md"


class Goal2009PreparedCupyTriangleLookupCacheTest(unittest.TestCase):
    def test_prepared_wrapper_caches_triangle_lookup_in_partner_layer(self) -> None:
        text = ADAPTER.read_text(encoding="utf-8")

        self.assertIn("self._cupy_exact_filter_triangle_lookup_cache", text)
        self.assertIn("triangle_lookup_cache: dict[str, object] | None = None", text)
        self.assertIn("triangle_lookup_cache.get(\"sorted_triangle_pos\")", text)
        self.assertIn("triangle_lookup_cache[\"sorted_triangle_ids\"]", text)
        self.assertIn("write_device_any_hit_all_witnesses", text)

    def test_report_keeps_boundary_and_records_pod_result(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: pod-pass-with-boundary", report)
        self.assertIn("Python partner layer", report)
        self.assertIn("0.002519239", report)
        self.assertIn("1.38x", report)
        self.assertIn("0.003932310", report)
        self.assertIn("2.46x", report)
        self.assertIn("does not authorize v2.0 release readiness", report)
        self.assertIn("goal2010_claude_review_goal2009", report)

    def test_pod_artifact_records_cached_prepared_speedup_and_parity(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(artifact["status"], "pass")
        self.assertEqual(artifact["count"], 2048)
        self.assertTrue(artifact["parity"]["strict_priority_flags_match"])
        prepared = artifact["partners"]["cupy"]["goal1889_prepared_reuse"]
        self.assertLess(prepared["query_median_ratio_vs_v1_8_prepared_native"], 0.75)
        self.assertLess(prepared["query_median_ratio_vs_goal1869_unprepared_partner"], 0.8)
        self.assertEqual(
            prepared["metadata"]["app_count_materialization"],
            "partner_gpu_unique_pair_counts_from_prepared_cupy_exact_filter",
        )
        self.assertTrue(prepared["metadata"]["whole_app_true_zero_copy_authorized"])
        self.assertFalse(artifact["claim_boundary"]["v2_0_release_authorized"])

    def test_larger_pod_artifact_records_scaling_gain(self) -> None:
        artifact = json.loads(ARTIFACT_4096.read_text(encoding="utf-8"))

        self.assertEqual(artifact["status"], "pass")
        self.assertEqual(artifact["count"], 4096)
        self.assertTrue(artifact["parity"]["strict_priority_flags_match"])
        prepared = artifact["partners"]["cupy"]["goal1889_prepared_reuse"]
        self.assertLess(prepared["query_median_ratio_vs_v1_8_prepared_native"], 0.5)
        self.assertLess(prepared["query_median_ratio_vs_goal1869_unprepared_partner"], 0.7)

    def test_claude_review_accepts_cache_boundary(self) -> None:
        review = CLAUDE_REVIEW.read_text(encoding="utf-8")

        self.assertIn("Verdict: **accept**", review)
        self.assertIn("Cache Lives Only in the Python Partner Wrapper", review)
        self.assertIn("Cache Safety and Exact-Filter Semantics", review)
        self.assertIn("Claim boundary flags", review)


if __name__ == "__main__":
    unittest.main()
