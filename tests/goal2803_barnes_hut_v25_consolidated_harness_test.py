from __future__ import annotations

import json
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
CLEAN_POD_ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2803_pod_artifacts"
    / "barnes_hut_v25_consolidated_harness_clean_from_git.json"
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

    def test_clean_pod_artifact_records_default_case_validation(self) -> None:
        payload = json.loads(CLEAN_POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["source_dirty"], [])
        self.assertEqual(payload["source_commit"], "60237c663c64b3322310817f0e0ece28e15e0f30")
        self.assertEqual(payload["repeats"], 3)
        self.assertEqual(payload["vector_warmups"], 2)
        self.assertEqual(len(payload["membership_rows"]), 3)
        self.assertEqual(
            payload["membership_validation_policy"],
            "first_case_reference_validation_plus_all_case_embree_optix_shape_parity",
        )
        self.assertTrue(all(row["rows_match_between_backends"] for row in payload["membership_rows"]))
        self.assertTrue(all(row["optix_rt_core_accelerated"] for row in payload["membership_rows"]))
        self.assertGreater(payload["max_optix_membership_speedup_vs_embree"], 100.0)
        self.assertTrue(payload["vector_sum"]["matches_torch"])
        self.assertTrue(payload["vector_sum"]["torch_faster"])

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
