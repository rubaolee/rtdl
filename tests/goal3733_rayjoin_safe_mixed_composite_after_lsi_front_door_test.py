import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3733_rayjoin_safe_mixed_composite_after_lsi_front_door_2026-06-07.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3733_rayjoin_safe_mixed_composite_after_lsi_front_door_a5000" / "summary.json"


class Goal3733RayJoinSafeMixedCompositeAfterLsiFrontDoorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.row = cls.payload["rows"][0]
        cls.workloads = {row["workload"]: row for row in cls.row["workloads"]}

    def test_composite_artifact_is_clean_and_count_matching(self):
        self.assertEqual("7a1c3248", self.payload["git_commit"][:8])
        self.assertEqual("", self.payload["git_status_short"])
        self.assertEqual([4096], self.payload["counts"])
        self.assertTrue(self.payload["summary"]["all_counts_match"])
        self.assertGreater(
            float(self.payload["summary"]["geomean_recommended_safe_mixed_speedup_vs_all_cupy"]),
            240.0,
        )
        self.assertIn("Tracked git status | clean", self.report)

    def test_lsi_uses_segment_pair_front_door_and_is_no_longer_bottleneck(self):
        lsi = self.workloads["lsi"]
        route = lsi["recommended_route"]["segment_pair_count_route"]
        timings = lsi["recommended_route"]["native_phase_timings"]
        self.assertEqual(
            "rtdl.optix.segment_pair_prepared_left_exact_intersection_count.front_door.v1",
            route["front_door_schema"],
        )
        self.assertEqual("SEGMENT_PAIR_INTERSECTION_ROWS_2D", route["primitive"])
        self.assertEqual("scalar_exact_count", route["output_contract"])
        self.assertEqual("count_prepared_left_grouped_range_direct_intersection", timings["mode"])
        self.assertGreater(float(lsi["recommended_speedup_vs_cupy"]), 12000.0)
        self.assertLess(float(lsi["recommended_route"]["hot_median_sec"]), 0.0002)
        self.assertIn("RTDL/OptiX exact segment-pair front door", self.report)

    def test_overlay_is_now_next_bottleneck(self):
        overlay = self.workloads["overlay_seed"]
        lsi = self.workloads["lsi"]
        self.assertGreater(
            float(overlay["recommended_route"]["hot_median_sec"]),
            float(lsi["recommended_route"]["hot_median_sec"]),
        )
        self.assertGreater(float(overlay["recommended_speedup_vs_cupy"]), 30.0)
        self.assertIn("next RayJoin performance target is overlay active-count", self.report)

    def test_claim_boundaries_remain_false(self):
        for key, value in self.payload["claim_boundary"].items():
            self.assertFalse(value, key)
        for workload in self.row["workloads"]:
            for key, value in workload["claim_boundary"].items():
                self.assertFalse(value, f"{workload['workload']}:{key}")
        self.assertIn("does not authorize", self.report)


if __name__ == "__main__":
    unittest.main()
