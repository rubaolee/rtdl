from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1072PostScaleUpRtxPodBatchTest(unittest.TestCase):
    def test_manifest_uses_goal1071_scales_and_excludes_barnes_hut(self) -> None:
        module = __import__("scripts.goal1072_post_scale_up_rtx_pod_batch", fromlist=["build_manifest"])
        payload = module.build_manifest()
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["summary"]["row_count"], 4)
        self.assertEqual(payload["summary"]["app_count"], 2)
        self.assertEqual(payload["summary"]["validation_row_count"], 2)
        self.assertEqual(payload["summary"]["timing_row_count"], 2)
        self.assertEqual(payload["summary"]["excluded_row_count"], 1)
        self.assertEqual(payload["summary"]["validation_rows_with_skip_validation"], [])
        self.assertEqual(payload["summary"]["timing_rows_without_floor"], [])
        self.assertIn("does not run cloud", payload["boundary"])
        self.assertIn("does not authorize public RTX speedup claims", payload["boundary"])

        excluded = payload["excluded_rows"][0]
        self.assertEqual(excluded["app"], "barnes_hut_force_app")
        self.assertEqual(excluded["exclusion_status"], "blocked_contract_reframe_required")
        self.assertIn("four one-level quadtree nodes", excluded["reason"])

    def test_rows_have_correct_validation_and_timing_policy(self) -> None:
        module = __import__("scripts.goal1072_post_scale_up_rtx_pod_batch", fromlist=["build_manifest"])
        rows = module.build_manifest()["rows"]
        by_key = {(row["app"], row["phase"]): row for row in rows}

        for app in ("facility_knn_assignment", "robot_collision_screening"):
            validation = by_key[(app, "correctness_validation")]
            timing = by_key[(app, "large_timing_repeat")]
            self.assertFalse(validation["contains_skip_validation"], app)
            self.assertTrue(timing["contains_skip_validation"], app)
            self.assertEqual(timing["timing_floor_sec"], 0.100)
            self.assertEqual(timing["source_goal"], "Goal1071")

        facility = by_key[("facility_knn_assignment", "large_timing_repeat")]
        self.assertIn("2500000", facility["command"])
        self.assertIn("facility_coverage_threshold_2_5m_timing.json", facility["output_json"])
        self.assertIn("goal1071_scale_up_probes", facility["source_evidence"])

        robot = by_key[("robot_collision_screening", "large_timing_repeat")]
        self.assertIn("36000000", robot["command"])
        self.assertIn("robot_prepared_pose_flags_36m_timing.json", robot["output_json"])
        self.assertIn("goal1071_scale_up_probes", robot["source_evidence"])

    def test_cli_writes_manifest_markdown_and_runner(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "manifest.json"
            output_md = Path(tmpdir) / "manifest.md"
            output_sh = Path(tmpdir) / "runner.sh"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1072_post_scale_up_rtx_pod_batch.py",
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
            self.assertEqual(payload["summary"]["row_count"], 4)
            markdown = output_md.read_text(encoding="utf-8")
            self.assertIn("Goal1072 Post-Scale-Up RTX Pod Batch", markdown)
            self.assertIn("blocked_contract_reframe_required", markdown)
            runner = output_sh.read_text(encoding="utf-8")
            self.assertIn("RTDL_SOURCE_COMMIT", runner)
            self.assertIn("nvidia-smi", runner)
            self.assertIn("2500000", runner)
            self.assertIn("36000000", runner)
            self.assertNotIn("barnes_hut_node_coverage", runner)


if __name__ == "__main__":
    unittest.main()
