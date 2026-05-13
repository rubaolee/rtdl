from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1933_goal1934_large_scale_all_app_v2_pod_perf_2026-05-13.md"
FIXED = ROOT / "docs" / "reports" / "goal1934_fixed_radius_huge_v2_pod" / "fixed_radius_524288.json"
LARGE = ROOT / "docs" / "reports" / "goal1933_large_scale_v2_pod_batch"


class Goal1933Goal1934LargeScaleAllAppV2PodPerfTest(unittest.TestCase):
    def test_fixed_radius_huge_artifact_is_seconds_scale_and_positive(self) -> None:
        payload = json.loads(FIXED.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["query_count"], 524288)
        self.assertEqual(payload["search_count"], 524288)
        self.assertEqual(len(payload["results"]), 12)
        for row in payload["results"]:
            with self.subTest(app=row["app"], partner=row["partner"]):
                forward = row["forward"]
                self.assertGreaterEqual(forward["v1_8_prepared_optix"]["median_s"], 1.0)
                self.assertLess(forward["v2_vs_v1_8_prepared_ratio"], 0.002)
                self.assertTrue(forward["parity"]["counts_match"])
                self.assertTrue(forward["parity"]["summary_match"])

    def test_control_artifacts_are_present_and_seconds_scale(self) -> None:
        db = json.loads((LARGE / "control_database_analytics_100000.json").read_text(encoding="utf-8"))
        graph = json.loads((LARGE / "control_graph_analytics_100000.json").read_text(encoding="utf-8"))
        pair = json.loads((LARGE / "control_polygon_pair_overlap_8192.json").read_text(encoding="utf-8"))
        jaccard = json.loads((LARGE / "control_polygon_jaccard_8192.json").read_text(encoding="utf-8"))

        self.assertGreaterEqual(db["results"][0]["prepared_session_warm_query_sec"]["median_sec"], 1.0)
        self.assertGreaterEqual(graph["phase_seconds"]["native_query"], 1.0)
        self.assertGreaterEqual(pair["phases"]["optix_candidate_discovery_sec"], 1.0)
        self.assertGreaterEqual(jaccard["phases"]["optix_candidate_discovery_sec"], 1.0)
        self.assertTrue(pair["parity_vs_cpu"])
        self.assertTrue(jaccard["parity_vs_cpu"])

    def test_report_keeps_claim_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: large-scale-evidence-collected-release-still-blocked", text)
        self.assertIn("not ranked KNN", text)
        self.assertIn("not v2 partner acceleration rows", text)
        self.assertIn("not a v2", text)
        self.assertIn("partner columnar scan/grouped-reduction implementation", text)
        self.assertIn("does not authorize v2.0", text)
        self.assertIn("release, whole-app speedup wording", text)
        self.assertIn("whole-app speedup wording", text)


if __name__ == "__main__":
    unittest.main()
