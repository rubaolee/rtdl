from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1166PostGoal1165NextPodPacketTest(unittest.TestCase):
    def test_manifest_targets_goal1165_followup_rows(self) -> None:
        module = __import__("scripts.goal1166_post_goal1165_next_pod_packet", fromlist=["build_manifest"])
        payload = module.build_manifest()

        self.assertTrue(payload["valid"])
        self.assertEqual(payload["summary"]["row_count"], 6)
        self.assertEqual(payload["summary"]["app_count"], 3)
        self.assertEqual(payload["summary"]["timing_row_count"], 2)
        self.assertEqual(payload["summary"]["timing_rows_without_skip_validation"], [])
        self.assertEqual(payload["summary"]["timing_rows_without_floor"], [])
        self.assertIn("does not authorize public wording", payload["boundary"])

    def test_rows_encode_expected_validation_policy(self) -> None:
        module = __import__("scripts.goal1166_post_goal1165_next_pod_packet", fromlist=["build_manifest"])
        rows = {row["label"]: row for row in module.build_manifest()["rows"]}

        self.assertFalse(rows["ann_candidate_validation"]["contains_skip_validation"])
        self.assertTrue(rows["ann_candidate_large_timing"]["contains_skip_validation"])
        self.assertIn("65536", rows["ann_candidate_large_timing"]["command"])
        self.assertEqual(rows["ann_candidate_large_timing"]["timing_floor_sec"], 0.100)

        self.assertFalse(rows["robot_pose_flags_validation"]["contains_skip_validation"])
        self.assertIn("32768", rows["robot_pose_flags_validation"]["command"])
        self.assertIn("python_objects", rows["robot_pose_flags_validation"]["command"])

        self.assertTrue(rows["robot_pose_flags_large_timing"]["contains_skip_validation"])
        self.assertIn("262144", rows["robot_pose_flags_large_timing"]["command"])
        self.assertIn("packed_arrays", rows["robot_pose_flags_large_timing"]["command"])
        self.assertIn("pose_count", rows["robot_pose_flags_large_timing"]["command"])

        self.assertIn("512", rows["jaccard_safe_chunk_validation"]["command"])
        self.assertIn("256", rows["jaccard_boundary_diagnostic_small_chunk"]["command"])
        self.assertIn("Expected to fail", rows["jaccard_boundary_diagnostic_small_chunk"]["expected_goal1165_effect"])

    def test_cli_writes_manifest_markdown_and_runner(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "manifest.json"
            output_md = Path(tmpdir) / "manifest.md"
            output_sh = Path(tmpdir) / "runner.sh"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1166_post_goal1165_next_pod_packet.py",
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
            self.assertEqual(payload["summary"]["row_count"], 6)
            markdown = output_md.read_text(encoding="utf-8")
            self.assertIn("Goal1166 Post-Goal1165 Next RTX Pod Packet", markdown)
            self.assertIn("ann_candidate_65536_timing.json", markdown)
            runner = output_sh.read_text(encoding="utf-8")
            self.assertIn("RTDL_OPTIX_PTX_COMPILER", runner)
            self.assertIn("Boundary diagnostic exit status", runner)
            self.assertIn("Goal1166 complete", runner)


if __name__ == "__main__":
    unittest.main()
