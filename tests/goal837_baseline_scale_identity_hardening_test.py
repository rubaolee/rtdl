from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal837BaselineScaleIdentityHardeningTest(unittest.TestCase):
    def test_two_ai_consensus_artifacts_exist(self) -> None:
        ledger = ROOT / "docs" / "reports" / "goal837_two_ai_consensus_2026-04-23.md"
        codex = ROOT / "docs" / "reports" / "goal837_codex_consensus_review_2026-04-23.md"
        gemini = ROOT / "docs" / "reports" / "goal837_gemini_external_consensus_review_2026-04-23.md"

        for path in (ledger, codex, gemini):
            self.assertTrue(path.exists(), str(path))

        text = ledger.read_text(encoding="utf-8")
        self.assertIn("Codex: ACCEPT", text)
        self.assertIn("Gemini 2.5 Flash: ACCEPT", text)
        self.assertIn("No Claude verdict is claimed", text)

    def test_report_records_scale_identity_boundary(self) -> None:
        report = ROOT / "docs" / "reports" / "goal837_baseline_scale_identity_hardening_2026-04-23.md"
        text = report.read_text(encoding="utf-8")
        self.assertIn("benchmark_scale", text)
        self.assertIn("small local smoke artifact", text)
        self.assertIn("does not run benchmarks", text)

    def test_goal835_plan_preserves_manifest_scale_for_active_entries(self) -> None:
        module = __import__("scripts.goal835_rtx_baseline_collection_plan", fromlist=["build_plan"])
        rows = {
            (row["app"], row["path_name"]): row
            for row in module.build_plan()["rows"]
        }
        self.assertEqual(
            rows[("robot_collision_screening", "prepared_pose_flags")]["scale"],
            {"pose_count": 200000, "obstacle_count": 1024, "iterations": 3},
        )
        self.assertEqual(
            rows[("database_analytics", "prepared_db_session_sales_risk")]["scale"],
            {"copies": 20000, "iterations": 10},
        )


if __name__ == "__main__":
    unittest.main()
