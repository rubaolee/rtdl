from __future__ import annotations

import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal2803_barnes_hut_v25_consolidated_harness.py"
REPORT = ROOT / "docs" / "reports" / "goal2803_barnes_hut_v2_5_consolidated_harness_2026-05-31.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal2803_barnes_hut_v2_5_consolidated_harness_consensus_2026-05-31.md"
POD_ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2803_pod_artifacts"
    / "barnes_hut_v25_consolidated_harness.json"
)


class Goal2803BarnesHutV25ConsolidatedHarnessTest(unittest.TestCase):
    def test_entrypoint_covers_membership_and_vector_sum_boundaries(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("run_goal2803_barnes_hut_consolidated_harness", text)
        self.assertIn("run_case", text)
        self.assertIn("grouped_vector_sum_2d_partner_columns", text)
        self.assertIn("triton_vector_sum_auto_selection_authorized", text)
        self.assertIn("native_engine_customization", text)

    def test_manifest_records_goal2803_barnes_hut_status(self) -> None:
        manifest = rt.v2_5_tiered_benchmark_manifest()
        row = next(app for app in manifest["apps"] if app["app_id"] == "barnes_hut")

        self.assertEqual(row["tier"], "B")
        self.assertEqual(row["canonical_harness_status"], "ready_with_goal2803_consolidated_harness")
        self.assertIn("Goal2803", row["pod_evidence_status"])
        self.assertIn("grouped-vector-sum", row["pod_evidence_status"])
        self.assertIn("auto-selection blocked", row["next_action"])
        self.assertEqual(rt.validate_v2_5_tiered_benchmark_manifest()["status"], "accept")

    def test_pod_artifact_records_rt_membership_and_vector_sum_boundary(self) -> None:
        text = POD_ARTIFACT.read_text(encoding="utf-8")

        self.assertIn('"status": "pass"', text)
        self.assertIn('"optix_rt_core_accelerated": true', text)
        self.assertIn('"rows_match_between_backends": true', text)
        self.assertIn('"triton_vector_sum_auto_selection_allowed": false', text)
        self.assertIn('"triton_vector_sum_auto_selection_authorized": false', text)
        self.assertIn('"native_engine_customization": false', text)

    def test_report_and_consensus_keep_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Barnes-Hut v2.5 Consolidated Harness", report)
        self.assertIn("Goal2803", consensus)
        self.assertIn("accept-with-boundary", consensus)
        self.assertIn("not a paper-reproduction claim", report)
        self.assertIn("Triton vector-sum auto-selection remains blocked", report)


if __name__ == "__main__":
    unittest.main()
