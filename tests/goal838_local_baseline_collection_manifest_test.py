from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal838LocalBaselineCollectionManifestTest(unittest.TestCase):
    def test_two_ai_consensus_artifacts_exist(self) -> None:
        ledger = ROOT / "docs" / "reports" / "goal838_two_ai_consensus_2026-04-23.md"
        codex = ROOT / "docs" / "reports" / "goal838_codex_consensus_review_2026-04-23.md"
        gemini = ROOT / "docs" / "reports" / "goal838_gemini_external_consensus_review_2026-04-23.md"

        for path in (ledger, codex, gemini):
            self.assertTrue(path.exists(), str(path))

        text = ledger.read_text(encoding="utf-8")
        self.assertIn("Codex: ACCEPT", text)
        self.assertIn("Gemini 2.5 Flash: ACCEPT", text)
        self.assertIn("No Claude verdict is claimed", text)

    def test_manifest_classifies_all_goal835_required_baselines(self) -> None:
        module = __import__("scripts.goal838_local_baseline_collection_manifest", fromlist=["build_collection_manifest"])
        payload = module.build_collection_manifest()
        self.assertEqual(payload["action_count"], 23)
        self.assertEqual(payload["status_counts"]["local_command_ready"], 10)
        self.assertEqual(payload["status_counts"]["linux_postgresql_required"], 2)
        self.assertEqual(payload["status_counts"]["deferred_until_app_gate_active"], 9)
        self.assertIn("does not run heavy benchmarks", payload["boundary"])

    def test_ready_commands_preserve_manifest_scale_and_artifact_paths(self) -> None:
        module = __import__("scripts.goal838_local_baseline_collection_manifest", fromlist=["build_collection_manifest"])
        payload = module.build_collection_manifest()
        ready = [action for action in payload["actions"] if action["status"] == "local_command_ready"]
        self.assertTrue(ready)
        db = next(
            action for action in ready
            if action["app"] == "database_analytics"
            and action["path_name"] == "prepared_db_session_sales_risk"
            and action["baseline"] == "cpu_oracle_compact_summary"
        )
        self.assertEqual(db["benchmark_scale"], {"copies": 20000, "iterations": 10})
        self.assertIn("--copies", db["command"])
        self.assertIn("20000", db["command"])
        self.assertEqual(db["collector_kind"], "goal840_db_prepared_baseline")
        self.assertEqual(db["command"][1], "scripts/goal840_db_prepared_baseline.py")
        self.assertTrue(db["artifact_path"].endswith("_cpu_oracle_compact_summary_2026-04-23.json"))

    def test_robot_actions_do_not_pretend_collector_exists_yet(self) -> None:
        module = __import__("scripts.goal838_local_baseline_collection_manifest", fromlist=["build_collection_manifest"])
        payload = module.build_collection_manifest()
        robot = [
            action for action in payload["actions"]
            if action["app"] == "robot_collision_screening"
        ]
        self.assertEqual({action["status"] for action in robot}, {"local_command_ready"})
        self.assertTrue(all(action["collector_kind"] == "goal839_robot_pose_count_baseline" for action in robot))
        self.assertTrue(all(action["command"][1] == "scripts/goal839_robot_pose_count_baseline.py" for action in robot))

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "manifest.json"
            output_md = Path(tmpdir) / "manifest.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal838_local_baseline_collection_manifest.py",
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertIn("Goal838 Local RTX Baseline Collection Manifest", completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["action_count"], 23)
            self.assertTrue(output_md.exists())


if __name__ == "__main__":
    unittest.main()
