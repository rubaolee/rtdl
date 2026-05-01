from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class Goal1078Goal1076ArtifactIntakeTest(unittest.TestCase):
    def test_missing_artifacts_require_cloud(self) -> None:
        module = __import__("scripts.goal1078_goal1076_artifact_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            payload = module.build_intake(Path(tmpdir))
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["overall_status"], "needs_cloud_artifacts")
        self.assertEqual(payload["expected_artifact_count"], 2)
        self.assertEqual(payload["missing_artifact_count"], 2)
        self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)

    def test_good_artifacts_reach_wording_review_only(self) -> None:
        module = __import__("scripts.goal1078_goal1076_artifact_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_dir = Path(tmpdir)
            _write_json(
                artifact_dir / "barnes_hut_rich_node_coverage_validation.json",
                {
                    "parameters": {"skip_validation": False, "barnes_tree_depth": 6, "hit_threshold": 4},
                    "scenario": {
                        "mode": "optix",
                        "result": {"matches_oracle": True, "node_count": 4096},
                    },
                },
            )
            _write_json(
                artifact_dir / "barnes_hut_rich_node_coverage_large_timing.json",
                {
                    "parameters": {"skip_validation": True, "barnes_tree_depth": 8, "hit_threshold": 4},
                    "scenario": {"timings_sec": {"optix_query_sec": {"median_sec": 0.123}}},
                },
            )
            payload = module.build_intake(artifact_dir)
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["overall_status"], "ready_for_public_wording_review")
        self.assertEqual(payload["validation_passed_count"], 1)
        self.assertEqual(payload["timing_floor_passed_count"], 1)
        self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)

    def test_bad_validation_artifact_blocks(self) -> None:
        module = __import__("scripts.goal1078_goal1076_artifact_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_dir = Path(tmpdir)
            _write_json(
                artifact_dir / "barnes_hut_rich_node_coverage_validation.json",
                {
                    "parameters": {"skip_validation": False, "barnes_tree_depth": 6, "hit_threshold": 4},
                    "scenario": {
                        "mode": "optix",
                        "result": {"matches_oracle": False, "node_count": 4096},
                    },
                },
            )
            payload = module.build_intake(artifact_dir)
        self.assertFalse(payload["valid"])
        self.assertEqual(payload["overall_status"], "blocked")
        self.assertEqual(payload["blocked_count"], 1)

    def test_wrong_depth_blocks(self) -> None:
        module = __import__("scripts.goal1078_goal1076_artifact_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_dir = Path(tmpdir)
            _write_json(
                artifact_dir / "barnes_hut_rich_node_coverage_validation.json",
                {
                    "parameters": {"skip_validation": False, "barnes_tree_depth": 5, "hit_threshold": 4},
                    "scenario": {
                        "mode": "optix",
                        "result": {"matches_oracle": True, "node_count": 1024},
                    },
                },
            )
            payload = module.build_intake(artifact_dir)
        self.assertFalse(payload["valid"])
        self.assertEqual(payload["overall_status"], "blocked")

    def test_missing_timing_median_blocks(self) -> None:
        module = __import__("scripts.goal1078_goal1076_artifact_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_dir = Path(tmpdir)
            _write_json(
                artifact_dir / "barnes_hut_rich_node_coverage_large_timing.json",
                {
                    "parameters": {"skip_validation": True, "barnes_tree_depth": 8, "hit_threshold": 4},
                    "scenario": {"timings_sec": {"optix_query_sec": {"min_sec": 0.1}}},
                },
            )
            payload = module.build_intake(artifact_dir)
        self.assertFalse(payload["valid"])
        self.assertEqual(payload["overall_status"], "blocked")

    def test_below_floor_is_not_claim_ready(self) -> None:
        module = __import__("scripts.goal1078_goal1076_artifact_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_dir = Path(tmpdir)
            _write_json(
                artifact_dir / "barnes_hut_rich_node_coverage_validation.json",
                {
                    "parameters": {"skip_validation": False, "barnes_tree_depth": 6, "hit_threshold": 4},
                    "scenario": {
                        "mode": "optix",
                        "result": {"matches_oracle": True, "node_count": 4096},
                    },
                },
            )
            _write_json(
                artifact_dir / "barnes_hut_rich_node_coverage_large_timing.json",
                {
                    "parameters": {"skip_validation": True, "barnes_tree_depth": 8, "hit_threshold": 4},
                    "scenario": {"timings_sec": {"optix_query_sec": {"median_sec": 0.01}}},
                },
            )
            payload = module.build_intake(artifact_dir)
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["overall_status"], "timing_floor_not_met")
        self.assertEqual(payload["timing_below_floor_count"], 1)
        self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)

    def test_cli_writes_intake_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "intake.json"
            output_md = Path(tmpdir) / "intake.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1078_goal1076_artifact_intake.py",
                    "--artifact-dir",
                    tmpdir,
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
            self.assertIn("needs_cloud_artifacts", completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["expected_artifact_count"], 2)
            markdown = output_md.read_text(encoding="utf-8")
            self.assertIn("Goal1078 Goal1076 Barnes-Hut Rich Artifact Intake", markdown)


if __name__ == "__main__":
    unittest.main()
