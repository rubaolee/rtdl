from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal835RtxBaselineCollectionPlanTest(unittest.TestCase):
    def test_two_ai_consensus_artifacts_exist(self) -> None:
        ledger = ROOT / "docs" / "reports" / "goal835_two_ai_consensus_2026-04-23.md"
        codex = ROOT / "docs" / "reports" / "goal835_codex_consensus_review_2026-04-23.md"
        gemini = ROOT / "docs" / "reports" / "goal835_gemini_external_consensus_review_2026-04-23.md"

        for path in (ledger, codex, gemini):
            self.assertTrue(path.exists(), str(path))

        ledger_text = ledger.read_text(encoding="utf-8")
        self.assertIn("Codex: ACCEPT", ledger_text)
        self.assertIn("Gemini 2.5 Flash: ACCEPT", ledger_text)
        self.assertIn("No Claude verdict is claimed", ledger_text)

    def test_plan_is_local_and_covers_active_and_deferred_entries(self) -> None:
        module = __import__("scripts.goal835_rtx_baseline_collection_plan", fromlist=["build_plan", "to_markdown"])
        payload = module.build_plan()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["active_count"], 8)
        self.assertEqual(payload["deferred_count"], 9)
        self.assertEqual(payload["row_count"], 17)
        self.assertIn("does not run benchmarks", payload["boundary"])

        markdown = module.to_markdown(payload)
        self.assertIn("database_analytics", markdown)
        self.assertIn("robot_collision_screening", markdown)
        self.assertIn("segment_polygon_hitcount", markdown)
        self.assertIn("facility_knn_assignment", markdown)
        self.assertIn("polygon_set_jaccard", markdown)
        self.assertIn("A public RTX speedup claim may not be made", markdown)

    def test_plan_rows_preserve_baseline_requirements(self) -> None:
        module = __import__("scripts.goal835_rtx_baseline_collection_plan", fromlist=["build_plan"])
        rows = {
            (row["app"], row["path_name"]): row
            for row in module.build_plan()["rows"]
        }

        db = rows[("database_analytics", "prepared_db_session_sales_risk")]
        self.assertIn("postgresql_same_semantics_on_linux_when_available", db["required_baselines"])
        self.assertIn("native_query", db["required_phases"])
        self.assertEqual(db["scale"], {"copies": 20000, "iterations": 10})

        fixed = rows[("outlier_detection", "prepared_fixed_radius_density_summary")]
        self.assertIn("cpu_scalar_threshold_count_oracle", fixed["required_baselines"])
        self.assertIn("not row-returning neighbors", fixed["claim_limit"])
        self.assertEqual(fixed["scale"], {"copies": 20000, "iterations": 10})

        robot = rows[("robot_collision_screening", "prepared_pose_flags")]
        self.assertIn("embree_anyhit_pose_count_or_equivalent_compact_summary", robot["required_baselines"])
        self.assertIn("native_anyhit_query", robot["required_phases"])
        self.assertEqual(robot["scale"], {"pose_count": 200000, "obstacle_count": 1024, "iterations": 3})

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "plan.json"
            output_md = Path(tmpdir) / "plan.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal835_rtx_baseline_collection_plan.py",
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
            self.assertIn("Goal835 RTX Baseline Collection Plan", completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "ok")
            self.assertTrue(output_md.exists())


if __name__ == "__main__":
    unittest.main()
