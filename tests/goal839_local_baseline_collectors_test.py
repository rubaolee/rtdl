from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal839LocalBaselineCollectorsTest(unittest.TestCase):
    def test_two_ai_consensus_artifacts_exist(self) -> None:
        ledger = ROOT / "docs" / "reports" / "goal839_two_ai_consensus_2026-04-23.md"
        codex = ROOT / "docs" / "reports" / "goal839_codex_consensus_review_2026-04-23.md"
        gemini = ROOT / "docs" / "reports" / "goal839_gemini_external_consensus_review_2026-04-23.md"

        for path in (ledger, codex, gemini):
            self.assertTrue(path.exists(), str(path))

        text = ledger.read_text(encoding="utf-8")
        self.assertIn("Codex: ACCEPT", text)
        self.assertIn("Gemini 2.5 Flash: ACCEPT", text)
        self.assertIn("No Claude verdict is claimed", text)

    def test_fixed_radius_cpu_outlier_artifact_matches_goal836_schema(self) -> None:
        module = __import__("scripts.goal839_fixed_radius_baseline", fromlist=["build_artifact"])
        artifact = module.build_artifact(
            app_name="outlier_detection",
            backend="cpu",
            copies=1,
            iterations=2,
        )
        self.assertEqual(artifact["status"], "ok")
        self.assertEqual(artifact["baseline_name"], "cpu_scalar_threshold_count_oracle")
        self.assertTrue(artifact["correctness_parity"])
        self.assertEqual(artifact["benchmark_scale"], {"copies": 1, "iterations": 2})
        self.assertIn("native_threshold_query", artifact["required_phase_coverage"])

    def test_fixed_radius_cpu_dbscan_artifact_matches_goal836_schema(self) -> None:
        module = __import__("scripts.goal839_fixed_radius_baseline", fromlist=["build_artifact"])
        artifact = module.build_artifact(
            app_name="dbscan_clustering",
            backend="cpu",
            copies=1,
            iterations=2,
        )
        self.assertEqual(artifact["status"], "ok")
        self.assertEqual(artifact["baseline_name"], "cpu_scalar_threshold_count_oracle")
        self.assertTrue(artifact["correctness_parity"])
        self.assertEqual(artifact["summary"]["core_count"], 7)

    def test_robot_cpu_pose_count_artifact_matches_goal836_schema(self) -> None:
        module = __import__("scripts.goal839_robot_pose_count_baseline", fromlist=["build_artifact"])
        artifact = module.build_artifact(
            backend="cpu",
            pose_count=8,
            obstacle_count=4,
            iterations=2,
        )
        self.assertEqual(artifact["status"], "ok")
        self.assertEqual(artifact["baseline_name"], "cpu_oracle_pose_count")
        self.assertTrue(artifact["correctness_parity"])
        self.assertIn("native_anyhit_query", artifact["required_phase_coverage"])
        self.assertEqual(artifact["summary"]["pose_count"], 8)

    def test_robot_cpu_pose_count_artifact_records_worker_count(self) -> None:
        module = __import__("scripts.goal839_robot_pose_count_baseline", fromlist=["build_artifact"])
        artifact = module.build_artifact(
            backend="cpu",
            pose_count=8,
            obstacle_count=4,
            iterations=1,
            worker_count=3,
        )
        self.assertEqual(artifact["validation"]["worker_count"], 3)
        self.assertIn("worker_count=3", " ".join(artifact["notes"]))

    def test_robot_pose_count_artifact_records_pose_id_start(self) -> None:
        module = __import__("scripts.goal839_robot_pose_count_baseline", fromlist=["build_artifact"])
        artifact = module.build_artifact(
            backend="cpu",
            pose_count=8,
            obstacle_count=4,
            iterations=1,
            pose_id_start=200001,
        )
        self.assertEqual(artifact["benchmark_scale"]["pose_id_start"], 200001)
        self.assertEqual(artifact["summary"]["colliding_pose_ids_sample"][0], 200002)

    def test_robot_summary_accepts_positional_native_ray_ids_with_pose_offset(self) -> None:
        baseline = __import__(
            "scripts.goal839_robot_pose_count_baseline",
            fromlist=["_summary_from_rows"],
        )
        robot_app = __import__(
            "examples.rtdl_robot_collision_screening_app",
            fromlist=["make_scaled_case"],
        )
        case = robot_app.make_scaled_case(
            pose_count=8,
            obstacle_count=4,
            pose_id_start=200001,
        )
        rows = (
            {"ray_id": 4, "any_hit": 1},
            {"ray_id": 5, "any_hit": 0},
        )

        summary = baseline._summary_from_rows(
            rows,
            case["poses"],
            case["edge_rays"],
            case["ray_metadata"],
        )

        self.assertEqual(summary["colliding_pose_ids_sample"], [200002])

    def test_robot_embree_timing_only_can_skip_cpu_oracle_validation(self) -> None:
        module = __import__("scripts.goal839_robot_pose_count_baseline", fromlist=["build_artifact"])
        artifact = module.build_artifact(
            backend="embree",
            pose_count=8,
            obstacle_count=4,
            iterations=1,
            skip_validation=True,
        )

        self.assertEqual(artifact["status"], "timing_only")
        self.assertIsNone(artifact["correctness_parity"])
        self.assertEqual(artifact["phase_seconds"]["oracle_validation_separate"], 0.0)
        self.assertTrue(artifact["validation"]["skipped"])
        self.assertIn("validation skipped", " ".join(artifact["notes"]))

    def test_cli_writes_artifact_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "artifact.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal839_fixed_radius_baseline.py",
                    "--app",
                    "outlier_detection",
                    "--backend",
                    "cpu",
                    "--copies",
                    "1",
                    "--iterations",
                    "2",
                    "--output-json",
                    str(output_json),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertIn('"status": "ok"', completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["baseline_name"], "cpu_scalar_threshold_count_oracle")

    def test_robot_embree_skip_validation_cli_writes_timing_only_successfully(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "nested" / "robot_timing_only.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal839_robot_pose_count_baseline.py",
                    "--backend",
                    "embree",
                    "--pose-count",
                    "8",
                    "--obstacle-count",
                    "4",
                    "--iterations",
                    "1",
                    "--skip-validation",
                    "--output-json",
                    str(output_json),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertIn('"status": "timing_only"', completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "timing_only")
            self.assertIsNone(payload["correctness_parity"])
            self.assertTrue(payload["validation"]["skipped"])


if __name__ == "__main__":
    unittest.main()
