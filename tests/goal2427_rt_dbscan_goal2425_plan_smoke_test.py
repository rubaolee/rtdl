from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2427_rt_dbscan_goal2425_plan_smoke_pod"
REPORT = ROOT / "docs" / "reports" / "goal2427_rt_dbscan_goal2425_plan_smoke_2026-05-19.md"

PREPARED_CUPY = "partner_cupy_prepared_grid_components_3d"
PREPARED_RT = "optix_rt_core_flags_cupy_prepared_grid_components_3d"


class Goal2427RtDbscanGoal2425PlanSmokeTest(unittest.TestCase):
    def test_summary_records_expected_goal2425_plan_choices(self) -> None:
        summary = json.loads((ARTIFACT_DIR / "summary.json").read_text(encoding="utf-8"))
        rows = {
            (row["dataset"], int(row["point_count"])): row
            for row in summary["rows"]
        }

        self.assertEqual(rows[("tiny", 9)]["selected_mode"], "cpu_reference")
        self.assertEqual(rows[("clustered3d", 32768)]["selected_mode"], PREPARED_CUPY)
        self.assertEqual(rows[("clustered3d", 65536)]["selected_mode"], PREPARED_RT)
        self.assertEqual(rows[("road3d", 262144)]["selected_mode"], PREPARED_CUPY)
        self.assertEqual(rows[("road3d", 524288)]["selected_mode"], PREPARED_RT)
        self.assertEqual(rows[("ngsim_dense", 131072)]["selected_mode"], PREPARED_CUPY)
        self.assertFalse(summary["claim_boundary"]["hidden_dispatcher"])
        self.assertFalse(summary["claim_boundary"]["paper_reproduction_claim_authorized"])

    def test_each_artifact_exposes_execution_plan_and_boundary(self) -> None:
        for artifact in ARTIFACT_DIR.glob("*.json"):
            if artifact.name == "summary.json":
                continue
            with self.subTest(artifact=artifact.name):
                payload = json.loads(artifact.read_text(encoding="utf-8"))
                self.assertEqual(payload["mode"], "planned_rt_dbscan")
                self.assertEqual(payload["selected_mode"], payload["metadata"]["execution_plan"]["selected_mode"])
                self.assertTrue(payload["metadata"]["execution_plan"]["not_hidden_dispatcher"])
                self.assertFalse(payload["claim_boundary"]["automatic_hidden_dispatcher"])
                self.assertFalse(payload["claim_boundary"]["paper_speedup_claim_authorized"])

    def test_report_keeps_deeper_runtime_problem_separate(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("plan -> explain -> execute -> preserve claim boundary", report)
        self.assertIn("correctness and planning problem is now closed", report)
        self.assertIn("deeper performance problem is still open", report)
        self.assertIn("not a DBSCAN-specific engine", report)


if __name__ == "__main__":
    unittest.main()
