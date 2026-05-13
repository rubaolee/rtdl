from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1940_robot_segment_scaleup_pod_perf_2026-05-13.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal1940_robot_segment_scaleup_pod"
SOURCE_LABEL = "35666fb829a88f77ebdc6d18b9a66a45861d0e67"


class Goal1940RobotSegmentScaleupPodPerfTest(unittest.TestCase):
    def _load(self, name: str) -> dict:
        return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))

    def test_segment_scaleup_reaches_seconds_scale_with_parity(self) -> None:
        payload = self._load("segment_1048576_segment_anyhit_rows_1048576.json")

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["source_commit_label"], SOURCE_LABEL)
        self.assertEqual(payload["gpu"], "NVIDIA RTX A5000, 570.195.03")
        self.assertEqual(payload["count"], 1048576)
        self.assertTrue(payload["parity"]["strict_rows_match"])
        self.assertGreaterEqual(payload["baseline"]["query_summary"]["median_s"], 7.0)
        self.assertFalse(payload["claim_boundary"]["v2_0_release_authorized"])
        self.assertFalse(payload["claim_boundary"]["whole_app_speedup_claim_authorized"])

        for partner, row in payload["partners"].items():
            with self.subTest(partner=partner):
                self.assertEqual(row["row_count"], 1048576)
                self.assertGreaterEqual(row["query_summary"]["median_s"], 1.0)
                self.assertLess(row["query_median_ratio_vs_v1_8_native"], 0.24)

    def test_robot_scaleup_has_exact_pose_flags_but_not_seconds_scale(self) -> None:
        payload = self._load("robot_8388608x16384_robot_collision_8388608x16384.json")

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["source_commit_label"], SOURCE_LABEL)
        self.assertEqual(payload["gpu"], "NVIDIA RTX A5000, 570.195.03")
        self.assertFalse(payload["claim_boundary"]["v2_0_release_authorized"])
        self.assertFalse(payload["claim_boundary"]["whole_app_speedup_claim_authorized"])

        for row in payload["results"]:
            with self.subTest(partner=row["partner"]):
                self.assertEqual(row["pose_count"], 8388608)
                self.assertEqual(row["obstacle_count"], 16384)
                self.assertTrue(row["parity"]["pose_collision_flags_match"])
                self.assertTrue(row["parity"]["colliding_pose_count_match"])
                self.assertLess(row["v2_vs_v1_8_prepared_ratio"], 0.021)
                self.assertLess(row["v1_8_prepared_optix_pose_flags"]["median_s"], 1.0)
                self.assertTrue(row["metadata"]["true_zero_copy_authorized"])
                self.assertFalse(row["metadata"]["rt_core_speedup_claim_authorized"])
                self.assertFalse(row["metadata"]["whole_app_speedup_claim_authorized"])

    def test_report_preserves_narrow_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: robot-segment-scaleup-evidence-collected-release-still-blocked", text)
        self.assertIn("1,048,576 | CuPy | 7.121871 | 1.631535 | 0.229088x", text)
        self.assertIn("8,388,608 | 16,384 | CuPy | 0.524696 | 0.009835 | 0.018745x", text)
        self.assertIn("not yet the seconds-scale robot claim", text)
        self.assertIn("does not authorize v2.0 release readiness", text)
        self.assertIn("broad RT-core", text)
        self.assertIn("arbitrary partner", text)


if __name__ == "__main__":
    unittest.main()
