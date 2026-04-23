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


if __name__ == "__main__":
    unittest.main()
