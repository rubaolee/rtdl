from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3764_robot_collision_hiprt_cuda_path_app_smoke.py"
REPORT = ROOT / "docs" / "reports" / "goal3764_robot_collision_hiprt_cuda_path_app_smoke_2026-06-07.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3764_robot_collision_hiprt_cuda_path_app_smoke_a5000.json"


class Goal3764RobotCollisionHiprtCudaPathAppSmokeTest(unittest.TestCase):
    def test_probe_script_uses_public_app_and_keeps_claim_boundary(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("rtdl.goal3764.robot_collision_hiprt_cuda_path_app_smoke.v1", text)
        self.assertIn("rtdl_robot_collision_screening_app", text)
        self.assertIn('app.run_app("hiprt"', text)
        self.assertIn('"amd_hardware_perf_claim_authorized": False', text)
        self.assertIn('"app_specific_native_engine_logic_allowed": False', text)
        self.assertIn("skip_validation=True", text)
        self.assertIn("all_correctness_cases_match_oracle", text)

    def test_report_and_artifact_when_present_are_bounded(self) -> None:
        if not REPORT.exists() or not ARTIFACT.exists():
            self.skipTest("Goal3764 pod artifact/report not generated yet")
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "rtdl.goal3764.robot_collision_hiprt_cuda_path_app_smoke.v1")
        self.assertTrue(payload["summary"]["all_correctness_cases_match_oracle"])
        self.assertEqual(payload["summary"]["correctness_case_count"], 2)
        self.assertGreaterEqual(payload["summary"]["max_timing_pose_count"], 512)
        self.assertFalse(payload["claim_boundary"]["amd_hardware_perf_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["release_authorized"])
        for row in payload["timings"]:
            self.assertEqual(row["validation_mode"], "skipped")
            self.assertGreater(row["hot_median_sec"], 0.0)
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("not AMD hardware performance evidence", report)
        self.assertIn("public app route", report)


if __name__ == "__main__":
    unittest.main()
