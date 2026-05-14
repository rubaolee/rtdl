from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2030_large_scale_v2_dev_pod_findings_2026-05-14.md"
JSON_REPORT = ROOT / "docs" / "reports" / "goal2030_large_scale_v2_dev_pod_findings_2026-05-14.json"
GOAL2028 = ROOT / "docs" / "reports" / "goal2028_large_scale_dev_pod_sweep_936aff2f"
GOAL2029 = ROOT / "docs" / "reports" / "goal2029_targeted_large_dev_pod_sweep_936aff2f"


class Goal2030LargeScaleV2DevPodFindingsTest(unittest.TestCase):
    def test_report_records_large_scale_wins_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("database analytics | 500k", text)
        self.assertIn("robot collision | 16,777,216", text)
        self.assertIn("road hazard prepared-only | 16,384", text)
        self.assertIn("not release authorization", text)
        self.assertIn("Do not claim", text)

    def test_report_records_design_debts(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Polygon Needs Tiling", text)
        self.assertIn("dense all-pairs", text)
        self.assertIn("Segment Materialized Rows Are Not The Right Large-Scale Contract", text)
        self.assertIn("CUDA 13 NVRTC/PTX", text)
        self.assertIn("benchmark modes", text)

    def test_json_pins_key_results_and_blocks_release_claims(self) -> None:
        payload = json.loads(JSON_REPORT.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "development-evidence-not-release-authorization")
        self.assertLess(payload["key_results"]["database_500k_ratio"], 0.21)
        self.assertLess(payload["key_results"]["robot_16m_ratio"], 0.02)
        self.assertLess(payload["key_results"]["road_hazard_16384_prepared_ratio"], 0.15)
        self.assertEqual(payload["key_results"]["polygon_16000_status"], "oom_dense_all_pairs_extent")
        self.assertGreater(payload["key_results"]["segment_1m_capacity_3x_ratio"], 1.0)
        self.assertFalse(payload["claim_boundary"]["v2_0_release_authorized"])
        self.assertFalse(payload["claim_boundary"]["whole_app_speedup_claim_authorized"])

    def test_required_artifacts_are_present(self) -> None:
        for path in (
            GOAL2028 / "database_control_cupy_500000.json",
            GOAL2028 / "graph_control_cupy_1000000_v2only.json",
            GOAL2028 / "robot_collision_cupy_16777216x16384.json",
            GOAL2028 / "segment_anyhit_cupy_1048576_capacity4194304.json",
            GOAL2028 / "fixed_radius_default_probe.log",
            GOAL2029 / "polygon_control_cupy_extent_12000.json",
            GOAL2029 / "road_hazard_prepared_only_16384.json",
            GOAL2029 / "segment_anyhit_cupy_1048576_capacity3145728.json",
        ):
            self.assertTrue(path.exists(), str(path))


if __name__ == "__main__":
    unittest.main()
