from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1080PostPodPublicWordingReadinessAuditTest(unittest.TestCase):
    def test_audit_blocks_public_wording_until_same_scale_baselines_exist(self) -> None:
        module = __import__("scripts.goal1080_post_pod_public_wording_readiness_audit", fromlist=["build_audit"])
        payload = module.build_audit()

        self.assertTrue(payload["valid"])
        self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)
        self.assertEqual(
            payload["decision_counts"],
            {
                "needs_same_scale_baseline_review": 2,
                "needs_reviewed_20m_validation_and_baseline": 1,
            },
        )

        rows = {row["app"]: row for row in payload["rows"]}
        self.assertEqual(rows["facility_knn_assignment"]["post_pod_status"], "ready_for_public_wording_review")
        self.assertEqual(rows["robot_collision_screening"]["post_pod_status"], "ready_for_public_wording_review")
        self.assertEqual(rows["facility_knn_assignment"]["decision"], "needs_same_scale_baseline_review")
        self.assertEqual(rows["robot_collision_screening"]["decision"], "needs_same_scale_baseline_review")
        self.assertFalse(rows["facility_knn_assignment"]["same_scale_baseline_available"])
        self.assertFalse(rows["robot_collision_screening"]["same_scale_baseline_available"])
        self.assertFalse(rows["barnes_hut_force_app"]["same_scale_baseline_available"])

    def test_scale_mismatch_is_explicit(self) -> None:
        module = __import__("scripts.goal1080_post_pod_public_wording_readiness_audit", fromlist=["build_audit"])
        rows = {row["app"]: row for row in module.build_audit()["rows"]}

        facility_scale = rows["facility_knn_assignment"]["scale"]
        self.assertEqual(facility_scale["rtx_copies"], 2_500_000)
        self.assertEqual(facility_scale["baseline_copies"], 20_000)

        robot_scale = rows["robot_collision_screening"]["scale"]
        self.assertEqual(robot_scale["rtx_pose_count"], 36_000_000)
        self.assertEqual(robot_scale["baseline_pose_count"], 200_000)
        self.assertEqual(robot_scale["rtx_obstacle_count"], 4096)
        self.assertEqual(robot_scale["baseline_obstacle_count"], 1024)

        barnes = rows["barnes_hut_force_app"]
        self.assertEqual(barnes["scale"]["probe_body_count"], 20_000_000)
        self.assertGreater(barnes["rtx_phase_sec_20m_probe"], 0.1)
        self.assertLess(barnes["rtx_phase_sec_1m"], 0.1)

    def test_cli_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "audit.json"
            output_md = Path(tmpdir) / "audit.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1080_post_pod_public_wording_readiness_audit.py",
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
            self.assertIn('"valid": true', completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)
            markdown = output_md.read_text(encoding="utf-8")
            self.assertIn("Goal1080 Post-Pod Public Wording Readiness Audit", markdown)
            self.assertIn("needs_same_scale_baseline_review", markdown)


if __name__ == "__main__":
    unittest.main()
