import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2060_v2_pod_mixed_family_audit_2026-05-15.md"
FIXED = ROOT / "docs" / "reports" / "goal2060_fixed_radius_family_cupy_l4_8192.json"
ROBOT = ROOT / "docs" / "reports" / "goal2060_robot_collision_cupy_l4_8192.json"
ROAD = ROOT / "docs" / "reports" / "goal2060_road_hazard_cupy_l4_1024.json"


class Goal2060V2PodMixedFamilyAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.fixed = json.loads(FIXED.read_text(encoding="utf-8"))
        cls.robot = json.loads(ROBOT.read_text(encoding="utf-8"))
        cls.road = json.loads(ROAD.read_text(encoding="utf-8"))

    def test_fixed_radius_family_is_positive_and_bounded(self):
        self.assertEqual(self.fixed["status"], "pass")
        self.assertEqual(self.fixed["gpu"], "NVIDIA L4, 570.195.03")
        self.assertFalse(self.fixed["claim_boundary"]["v2_0_release_authorized"])
        self.assertFalse(self.fixed["claim_boundary"]["whole_app_speedup_claim_authorized"])
        for row in self.fixed["results"]:
            self.assertEqual(row["status"], "pass")
            self.assertTrue(row["forward"]["parity"]["counts_match"])
            self.assertLess(row["forward"]["v2_vs_v1_8_prepared_ratio"], 1.0)
            if "reverse" in row:
                self.assertTrue(row["reverse"]["parity"]["counts_match"])
                self.assertLess(row["reverse"]["v2_vs_v1_8_prepared_ratio"], 1.0)

    def test_robot_collision_passes_parity_but_is_not_speedup(self):
        self.assertEqual(self.robot["status"], "pass")
        row = self.robot["results"][0]
        self.assertTrue(row["parity"]["colliding_pose_count_match"])
        self.assertTrue(row["parity"]["pose_collision_flags_match"])
        self.assertTrue(row["metadata"]["true_zero_copy_authorized"])
        self.assertGreater(row["v2_vs_v1_8_prepared_ratio"], 1.0)

    def test_road_hazard_passes_parity_but_prepared_path_is_not_speedup(self):
        self.assertEqual(self.road["status"], "pass")
        self.assertTrue(self.road["parity"]["strict_priority_flags_match"])
        cupy = self.road["partners"]["cupy"]
        self.assertTrue(cupy["metadata"]["whole_app_true_zero_copy_authorized"])
        self.assertLess(cupy["goal1889_prepared_reuse"]["query_median_ratio_vs_v1_8_one_shot_native"], 1.0)
        self.assertGreater(cupy["goal1889_prepared_reuse"]["query_median_ratio_vs_v1_8_prepared_native"], 1.0)

    def test_report_records_mixed_verdict_and_boundaries(self):
        required = [
            "mixed-result engineering audit",
            "threshold/summary proxy rows",
            "v2 is slower than the v1.8 prepared OptiX pose-flag path",
            "about 8.7% slower than v1.8 prepared",
            "prepared-only large-run mode",
            "v2.0 release readiness",
            "broad all-app speedup",
            "robot collision speedup",
            "road hazard prepared-path speedup",
            "`accept-with-boundary`",
        ]
        for phrase in required:
            self.assertIn(phrase, self.report)


if __name__ == "__main__":
    unittest.main()
