from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "robot_collision"
    / "rtdl_robot_collision_benchmark_app.py"
)
REPORT = ROOT / "docs" / "reports" / "goal3831_robot_collision_probe_reference_separation_scale_profile_2026-06-07.md"
GOAL3826 = ROOT / "docs" / "reports" / "goal3826_scale_profile_calibration_a5000_2026-06-07.md"
GOAL3827 = ROOT / "docs" / "reports" / "goal3827_scale_profile_file_stdout_correction_a5000_2026-06-07.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal3828_current_benchmark_scale_profiles_a5000" / "summary.json"


class Goal3831RobotCollisionProbeReferenceSeparationScaleProfileTest(unittest.TestCase):
    def test_app_exposes_explicit_no_probe_reference_mode(self) -> None:
        text = APP.read_text(encoding="utf-8")
        self.assertIn("--no-probe-reference", text)
        self.assertIn("validate_probe_reference: bool = True", text)
        self.assertIn('"probe_reference_validated"', text)
        self.assertIn('"probe_reference_seconds"', text)
        self.assertIn("matches_probe_reference = None", text)

    def test_scale_registry_uses_perf_only_robot_row(self) -> None:
        row = next(row for row in rt.current_benchmark_scale_profiles() if row["app"] == "robot_collision")
        self.assertEqual(row["row_id"], "robot_collision_optix_scale_default_1024_no_probe_reference")
        self.assertIn("--no-probe-reference", row["command"])
        self.assertIn("Goal3831", row["evidence_refs"])
        self.assertEqual(row["expected_runtime_class"], "default_scale_no_probe_reference")

    def test_prior_calibration_reports_point_to_goal3831_split(self) -> None:
        goal3826 = GOAL3826.read_text(encoding="utf-8")
        goal3827 = GOAL3827.read_text(encoding="utf-8")
        self.assertIn("Goal3831", goal3826)
        self.assertIn("Goal3831", goal3827)
        self.assertIn("--no-probe-reference", goal3827)
        self.assertIn("validation-heavy", goal3827)

    def test_report_records_non_authorizing_validation_separation(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3831",
            "CPU probe-reference pass",
            "validation-inclusive benchmark wall time",
            "--no-probe-reference",
            "does not weaken correctness requirements",
            "does not authorize release action",
        ):
            self.assertIn(phrase, text)

    def test_a5000_artifact_records_robot_probe_reference_separation(self) -> None:
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        row = next(row for row in payload["rows"] if row["app"] == "robot_collision")
        self.assertEqual(row["row_id"], "robot_collision_optix_scale_default_1024_no_probe_reference")
        self.assertEqual(row["status"], "pass")
        self.assertLess(row["elapsed_sec"], 5.0)
        self.assertIn("--no-probe-reference", row["command"])
        self.assertEqual(row["semantic_stdout_check"]["claim_flag_violations"], [])
        self.assertIn('"probe_reference_validated": false', row["stdout_tail"])
        self.assertIn('"probe_reference_signature": null', row["stdout_tail"])


if __name__ == "__main__":
    unittest.main()
