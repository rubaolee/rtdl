import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "rebuild" / "v3" / "evidence" / "v3_claim_grade_all_benchmarks_calibrated_20260620"
SUMMARY = ARTIFACT / "summary.json"
REPORT = ROOT / "docs" / "rebuild" / "v3" / "v3_claim_grade_all_benchmark_results_2026-06-20.md"


EXPECTED_APPS = {
    "hausdorff_xhd",
    "spatial_rayjoin",
    "rt_dbscan",
    "robot_collision",
    "raydb_style",
    "barnes_hut",
    "librts_spatial_index",
    "rtnn",
    "triangle_counting",
    "contact_manifold",
}


class V3ClaimGradeAllBenchmarksTest(unittest.TestCase):
    def payload(self):
        return json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_artifact_exists_and_all_rows_pass(self):
        payload = self.payload()
        self.assertEqual(payload["tool"], "v3_claim_grade_all_benchmarks")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertEqual(len(payload["rows"]), 40)
        self.assertEqual(Counter(row["status"] for row in payload["rows"]), {"ok": 40})
        self.assertEqual(set(payload["case_count_by_app"]), EXPECTED_APPS)
        self.assertTrue(all(payload["case_count_by_app"][app] > 0 for app in EXPECTED_APPS))

    def test_ratios_cover_every_app_with_non_toy_rows(self):
        payload = self.payload()
        ratios = payload["annotated_ratios"]
        self.assertEqual(len(ratios), 19)
        self.assertEqual({row["app_id"] for row in ratios}, EXPECTED_APPS)
        self.assertTrue(all(float(row["optix_speedup_vs_embree"]) > 1.0 for row in ratios))

        groups = {row["comparison_group"] for row in ratios}
        self.assertNotIn("rayjoin_all_backend_query_summary", groups)
        self.assertNotIn("aabb_index_all_count_only", groups)
        self.assertIn("rayjoin_overlay_seed_authored_tiled_x2048", groups)
        self.assertIn("aabb_index_all_count_only_large_32768", groups)
        self.assertIn("triangle_count_rt_graph_2a1_cliques_80000", groups)

    def test_report_keeps_boundaries_visible(self):
        text = REPORT.read_text(encoding="utf-8")
        for needle in [
            "40 rows / 40 ok / 0 failed",
            "all ten promoted benchmark apps",
            "release_authorized: false",
            "not release authorization",
            "not LibRTS authors-code",
            "RTDBSCAN remains internal after same-contract",
            "V3 broadly beats V2.x",
            "Superseded by same-contract rerun",
        ]:
            self.assertIn(needle, text)
        self.assertIn("not full rayjoin paper reproduction", text.lower())


if __name__ == "__main__":
    unittest.main()
