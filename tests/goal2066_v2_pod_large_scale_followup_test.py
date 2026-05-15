import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2066_v2_pod_large_scale_followup_2026-05-15.md"
REPORTS = ROOT / "docs" / "reports"


def _json(name: str) -> dict:
    return json.loads((REPORTS / name).read_text(encoding="utf-8"))


class Goal2066V2PodLargeScaleFollowupTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")

    def test_robot_scaling_turns_positive(self):
        small = _json("goal2066_robot_collision_cupy_l4_32768x8192.json")["results"][0]
        large = _json("goal2066_robot_collision_cupy_l4_65536x8192.json")["results"][0]
        self.assertTrue(small["parity"]["pose_collision_flags_match"])
        self.assertTrue(large["parity"]["pose_collision_flags_match"])
        self.assertLess(small["v2_vs_v1_8_prepared_ratio"], 0.2)
        self.assertLess(large["v2_vs_v1_8_prepared_ratio"], 0.1)
        self.assertTrue(large["metadata"]["true_zero_copy_authorized"])

    def test_compact_count_and_road_rows_are_strong(self):
        hitcount = _json("goal2066_segment_polygon_hitcount_cupy_l4_131072_capacity67108864.json")
        road = _json("goal2066_road_hazard_cupy_l4_12288_prepared_only.json")
        hit_cupy = hitcount["partners"]["cupy"]["goal1886_prepared_reuse"]
        road_cupy = road["partners"]["cupy"]["goal1889_prepared_reuse"]
        self.assertTrue(hitcount["parity"]["strict_counts_match"])
        self.assertLess(hit_cupy["query_median_ratio_vs_v1_8_prepared_native"], 0.01)
        self.assertTrue(road["parity"]["strict_priority_flags_match"])
        self.assertLess(road_cupy["query_median_ratio_vs_v1_8_prepared_native"], 0.1)

    def test_fixed_radius_family_remains_positive_but_bounded(self):
        payload = _json("goal2066_fixed_radius_family_cupy_l4_16384.json")
        self.assertEqual(payload["status"], "pass")
        ratios = []
        for row in payload["results"]:
            self.assertEqual(row["status"], "pass")
            ratios.append(row["forward"]["v2_vs_v1_8_prepared_ratio"])
            if "reverse" in row:
                ratios.append(row["reverse"]["v2_vs_v1_8_prepared_ratio"])
        self.assertTrue(ratios)
        self.assertTrue(all(ratio < 0.02 for ratio in ratios))
        self.assertIn("threshold proxy", self.report)

    def test_mixed_rows_remain_explicitly_blocked(self):
        anyhit = _json("goal2066_segment_polygon_anyhit_cupy_l4_4096_capacity16777216.json")
        poly2048 = _json("goal2066_polygon_rawkernel_cupy_optix_l4_2048.json")
        poly3072 = _json("goal2066_polygon_rawkernel_cupy_optix_l4_3072.json")
        self.assertTrue(anyhit["parity"]["strict_rows_match"])
        self.assertGreater(anyhit["partners"]["cupy"]["query_median_ratio_vs_v1_8_native"], 1.0)
        pair2048 = next(row for row in poly2048["results"] if row["app"] == "polygon_pair_overlap_area_rows")
        pair3072 = next(row for row in poly3072["results"] if row["app"] == "polygon_pair_overlap_area_rows")
        self.assertGreater(pair2048["v2_vs_v1_8_ratio"], 1.0)
        self.assertGreater(pair3072["v2_vs_v1_8_ratio"], 1.0)
        oom_log = (REPORTS / "goal2066_polygon_rawkernel_cupy_optix_l4_4096_oom.log").read_text(encoding="utf-8")
        self.assertIn("out of memory", oom_log.lower())

    def test_report_preserves_release_boundaries(self):
        required = [
            "`accept-with-boundary`",
            "not yet a clean v2.0 performance primitive",
            "not a timing anomaly",
            "claim all v2.0 apps are faster than v1.8",
            "claim v2.0 release readiness",
        ]
        for phrase in required:
            self.assertIn(phrase, self.report)


if __name__ == "__main__":
    unittest.main()
