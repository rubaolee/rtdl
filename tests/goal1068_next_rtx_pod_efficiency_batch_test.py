from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1068NextRtxPodEfficiencyBatchTest(unittest.TestCase):
    def test_batch_combines_goal1062_and_reviewed_barnes_candidate(self) -> None:
        module = __import__("scripts.goal1068_next_rtx_pod_efficiency_batch", fromlist=["build_manifest"])
        payload = module.build_manifest()
        self.assertTrue(payload["valid"])
        self.assertTrue(payload["goal1067_barnes_ready"])
        self.assertEqual(payload["summary"]["row_count"], 6)
        self.assertEqual(payload["summary"]["app_count"], 3)
        self.assertEqual(payload["summary"]["validation_row_count"], 3)
        self.assertEqual(payload["summary"]["timing_row_count"], 3)
        self.assertEqual(payload["summary"]["validation_rows_with_skip_validation"], [])
        self.assertEqual(payload["summary"]["timing_rows_without_floor"], [])
        self.assertIn("does not run cloud", payload["boundary"])
        self.assertIn("does not authorize public RTX speedup claims", payload["boundary"])

    def test_rows_have_correct_validation_and_timing_policy(self) -> None:
        module = __import__("scripts.goal1068_next_rtx_pod_efficiency_batch", fromlist=["build_manifest"])
        rows = module.build_manifest()["rows"]
        by_key = {(row["app"], row["phase"]): row for row in rows}

        for app in ("facility_knn_assignment", "robot_collision_screening", "barnes_hut_force_app"):
            validation = by_key[(app, "correctness_validation")]
            timing = by_key[(app, "large_timing_repeat")]
            self.assertFalse(validation["contains_skip_validation"], app)
            self.assertTrue(timing["contains_skip_validation"], app)
            self.assertEqual(timing["timing_floor_sec"], 0.100)

        barnes_validation = by_key[("barnes_hut_force_app", "correctness_validation")]
        self.assertIn("200000", barnes_validation["command"])
        self.assertIn("barnes_hut_node_coverage_validation.json", barnes_validation["output_json"])

        barnes_timing = by_key[("barnes_hut_force_app", "large_timing_repeat")]
        self.assertIn("1000000", barnes_timing["command"])
        self.assertIn("--skip-validation", barnes_timing["command"])
        self.assertEqual(barnes_timing["source_goal"], "Goal1067")

    def test_cli_writes_manifest_markdown_and_runner(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "manifest.json"
            output_md = Path(tmpdir) / "manifest.md"
            output_sh = Path(tmpdir) / "runner.sh"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1068_next_rtx_pod_efficiency_batch.py",
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
            self.assertIn("Goal1068 Next RTX Pod Efficiency Batch", markdown)
            self.assertIn("barnes_hut_node_coverage_1m_timing.json", markdown)
            runner = output_sh.read_text(encoding="utf-8")
            self.assertIn("RTDL_SOURCE_COMMIT", runner)
            self.assertIn("nvidia-smi", runner)
            self.assertIn("Goal1068 complete", runner)


if __name__ == "__main__":
    unittest.main()
