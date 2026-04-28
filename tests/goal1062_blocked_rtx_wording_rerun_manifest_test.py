from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1062BlockedRtxWordingRerunManifestTest(unittest.TestCase):
    def test_manifest_targets_only_remaining_blocked_public_wording_rows(self) -> None:
        module = __import__(
            "scripts.goal1062_blocked_rtx_wording_rerun_manifest",
            fromlist=["build_manifest"],
        )
        payload = module.build_manifest()
        self.assertTrue(payload["valid"])
        self.assertEqual(
            payload["blocked_apps"],
            ["facility_knn_assignment", "robot_collision_screening"],
        )
        self.assertEqual(payload["summary"]["row_count"], 4)
        self.assertEqual(payload["summary"]["validation_row_count"], 2)
        self.assertEqual(payload["summary"]["timing_row_count"], 2)
        self.assertEqual(payload["summary"]["validation_rows_with_skip_validation"], [])
        self.assertEqual(payload["summary"]["timing_rows_without_floor"], [])
        self.assertIn("does not run cloud", payload["boundary"])

    def test_validation_rows_do_not_skip_validation_and_timing_rows_have_floor(self) -> None:
        module = __import__(
            "scripts.goal1062_blocked_rtx_wording_rerun_manifest",
            fromlist=["build_manifest"],
        )
        rows = module.build_manifest()["rows"]
        by_key = {(row["app"], row["phase"]): row for row in rows}

        facility_validation = by_key[("facility_knn_assignment", "correctness_validation")]
        self.assertFalse(facility_validation["contains_skip_validation"])
        self.assertIn("facility_service_coverage", facility_validation["command"])

        facility_timing = by_key[("facility_knn_assignment", "large_timing_repeat")]
        self.assertTrue(facility_timing["contains_skip_validation"])
        self.assertEqual(facility_timing["timing_floor_sec"], 0.100)
        self.assertIn("800000", facility_timing["command"])

        robot_validation = by_key[("robot_collision_screening", "correctness_validation")]
        self.assertFalse(robot_validation["contains_skip_validation"])
        self.assertIn("python_objects", robot_validation["command"])
        self.assertIn("pose_flags", robot_validation["command"])

        robot_timing = by_key[("robot_collision_screening", "large_timing_repeat")]
        self.assertTrue(robot_timing["contains_skip_validation"])
        self.assertEqual(robot_timing["timing_floor_sec"], 0.100)
        self.assertIn("packed_arrays", robot_timing["command"])
        self.assertIn("pose_count", robot_timing["command"])
        self.assertIn("8000000", robot_timing["command"])

    def test_cli_writes_json_markdown_and_shell_runner(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "manifest.json"
            output_md = Path(tmpdir) / "manifest.md"
            output_sh = Path(tmpdir) / "runner.sh"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1062_blocked_rtx_wording_rerun_manifest.py",
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                    "--output-sh",
                    str(output_sh),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            self.assertIn('"valid": true', completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertTrue(payload["valid"])
            markdown = output_md.read_text(encoding="utf-8")
            self.assertIn("Goal1062 Blocked RTX Wording Rerun Manifest", markdown)
            self.assertIn("facility_coverage_threshold_large_timing.json", markdown)
            shell = output_sh.read_text(encoding="utf-8")
            self.assertIn("RTDL_SOURCE_COMMIT", shell)
            self.assertIn("nvidia-smi", shell)
            self.assertIn("Goal1062 complete", shell)


if __name__ == "__main__":
    unittest.main()
