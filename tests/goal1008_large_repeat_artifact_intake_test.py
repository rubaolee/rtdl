from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1008LargeRepeatArtifactIntakeTest(unittest.TestCase):
    def test_large_repeat_intake_keeps_public_claims_closed(self) -> None:
        module = __import__(
            "scripts.goal1008_large_repeat_artifact_intake",
            fromlist=["build_intake"],
        )
        payload = module.build_intake()
        self.assertEqual(payload["row_count"], 7)
        self.assertEqual(payload["timing_floor_cleared_count"], 6)
        self.assertEqual(payload["still_held_count"], 1)
        self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)
        self.assertIn("does not authorize any public speedup claim", payload["boundary"])

    def test_robot_remains_held_and_scaled_rows_clear_floor(self) -> None:
        module = __import__(
            "scripts.goal1008_large_repeat_artifact_intake",
            fromlist=["build_intake"],
        )
        rows = {
            (row["app"], row["path_name"]): row
            for row in module.build_intake()["rows"]
        }
        self.assertEqual(
            rows[("robot_collision_screening", "prepared_pose_flags")]["large_repeat_status"],
            "still_below_public_review_timing_floor",
        )
        self.assertLess(rows[("robot_collision_screening", "prepared_pose_flags")]["rtx_phase_sec"], 0.10)
        self.assertEqual(
            rows[("outlier_detection", "prepared_fixed_radius_density_summary")]["chosen_artifact"],
            "goal1007_outlier_dbscan_x35_large_rtx.json",
        )
        self.assertGreaterEqual(
            rows[("ann_candidate_search", "candidate_threshold_prepared")]["rtx_phase_sec"],
            0.10,
        )

    def test_cli_writes_report_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "goal1008.json"
            output_md = Path(tmpdir) / "goal1008.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1008_large_repeat_artifact_intake.py",
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            self.assertIn("Goal1008 Large-Repeat RTX Artifact Intake", completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["timing_floor_cleared_count"], 6)
            self.assertTrue(output_md.exists())


if __name__ == "__main__":
    unittest.main()
