from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1126RobotNormalizedPublicWordingReviewTest(unittest.TestCase):
    def test_packet_accepts_only_explicit_normalized_review_candidate(self) -> None:
        module = __import__(
            "scripts.goal1126_robot_normalized_public_wording_review",
            fromlist=["build_packet"],
        )
        payload = module.build_packet()

        self.assertTrue(payload["valid"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertEqual(
            payload["decision_under_review"],
            "accept_explicit_normalized_baseline_review",
        )
        self.assertEqual(
            payload["current_goal1123_robot_decision"],
            "keep_public_wording_blocked_pending_same_scale_baseline",
        )
        self.assertGreater(payload["normalized_ratio_embree_per_pose_over_rtx_per_pose"], 900.0)

    def test_checks_capture_scale_and_contract_boundaries(self) -> None:
        module = __import__(
            "scripts.goal1126_robot_normalized_public_wording_review",
            fromlist=["build_packet"],
        )
        checks = module.build_packet()["checks"]

        self.assertTrue(checks["same_obstacle_count"])
        self.assertTrue(checks["same_result_contract"])
        self.assertTrue(checks["separate_current_source_validation_ok"])
        self.assertTrue(checks["current_source_intake_ok"])
        self.assertTrue(checks["embree_chunked_baseline_ok"])
        self.assertTrue(checks["pose_counts_differ"])
        self.assertTrue(checks["wording_explicitly_normalized"])

    def test_markdown_does_not_overclaim_whole_app_or_same_total_work(self) -> None:
        module = __import__(
            "scripts.goal1126_robot_normalized_public_wording_review",
            fromlist=["build_packet", "to_markdown"],
        )
        markdown = module.to_markdown(module.build_packet())

        self.assertIn("normalized per-pose", markdown)
        self.assertIn("not a same-total-work wall-time claim", markdown)
        self.assertIn("whole-app planning speedup are outside", markdown)
        self.assertIn("does not edit public wording", markdown)

    def test_cli_writes_reproducible_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "goal1126.json"
            output_md = Path(tmpdir) / "goal1126.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1126_robot_normalized_public_wording_review.py",
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
            self.assertTrue(payload["valid"])
            self.assertIn(
                "Goal1126 Robot Normalized Public RTX Wording Review",
                output_md.read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
