from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1007LargerScaleRtxRepeatPlanTest(unittest.TestCase):
    def test_plan_covers_all_held_goal1006_candidates(self) -> None:
        module = __import__(
            "scripts.goal1007_larger_scale_rtx_repeat_plan",
            fromlist=["build_plan"],
        )
        payload = module.build_plan()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["held_candidate_count"], 7)
        self.assertEqual(payload["target_count"], 7)
        self.assertEqual(payload["executable_command_count"], 6)
        self.assertFalse(payload["missing_held_candidates"])
        self.assertFalse(payload["extra_targets"])
        self.assertEqual(payload["current_public_wording_source"], "rtdsl.rtx_public_wording_matrix()")
        self.assertIn("does not start cloud resources", payload["boundary"])
        self.assertIn("rtdsl.rtx_public_wording_matrix()", payload["boundary"])

    def test_commands_target_larger_scales_and_bounded_outputs(self) -> None:
        module = __import__(
            "scripts.goal1007_larger_scale_rtx_repeat_plan",
            fromlist=["build_plan"],
        )
        targets = {
            (row["app"], row["path_name"]): row
            for row in module.build_plan()["targets"]
        }
        robot = targets[("robot_collision_screening", "prepared_pose_flags")]["command"]
        self.assertIn("8000000", robot)
        self.assertIn("pose_count", robot)
        self.assertEqual(
            targets[("robot_collision_screening", "prepared_pose_flags")][
                "current_public_wording_status"
            ],
            "public_wording_blocked",
        )
        self.assertIn(
            "100 ms",
            targets[("robot_collision_screening", "prepared_pose_flags")][
                "current_public_wording_boundary"
            ],
        )

        pair_rows = targets[("segment_polygon_anyhit_rows", "segment_polygon_anyhit_rows_prepared_bounded_gate")]["command"]
        self.assertIn("--output-capacity", pair_rows)
        self.assertIn("131072", pair_rows)

        dbscan = targets[("dbscan_clustering", "prepared_fixed_radius_core_flags")]
        self.assertIn("reused_output_json", dbscan)

    def test_cli_writes_json_markdown_and_shell(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "goal1007.json"
            output_md = Path(tmpdir) / "goal1007.md"
            output_sh = Path(tmpdir) / "goal1007.sh"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1007_larger_scale_rtx_repeat_plan.py",
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
            self.assertIn("Goal1007 Larger-Scale RTX Repeat Plan", completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["target_count"], 7)
            shell_text = output_sh.read_text(encoding="utf-8")
            self.assertIn("already-running RTX pod", shell_text)
            self.assertIn("does not create cloud resources", shell_text)
            self.assertIn("goal1007_robot_pose_flags_large_rtx.json", shell_text)
            self.assertIn(
                "rtdsl.rtx_public_wording_matrix()",
                output_md.read_text(encoding="utf-8"),
            )

    def test_audit_existing_does_not_write_shell_without_explicit_output_sh(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "goal1007.json"
            output_md = Path(tmpdir) / "goal1007.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1007_larger_scale_rtx_repeat_plan.py",
                    "--audit-existing",
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
            self.assertIn("Existing Output Audit", completed.stdout)
            self.assertEqual(sorted(Path(tmpdir).iterdir()), [output_json, output_md])


if __name__ == "__main__":
    unittest.main()
