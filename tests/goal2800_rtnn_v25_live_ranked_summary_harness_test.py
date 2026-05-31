from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal2800_rtnn_v25_live_ranked_summary_harness.py"
REPORT = ROOT / "docs" / "reports" / "goal2800_rtnn_v2_5_live_ranked_summary_harness_2026-05-31.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal2800_rtnn_v2_5_live_ranked_summary_harness_consensus_2026-05-31.md"
POD_ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2800_pod_artifacts"
    / "rtnn_v25_live_ranked_summary_65536.json"
)
CLEAN_POD_ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2800_pod_artifacts"
    / "rtnn_v25_live_ranked_summary_65536_clean_from_git.json"
)


class Goal2800RtnnV25LiveRankedSummaryHarnessTest(unittest.TestCase):
    def test_harness_runs_rtdl_and_cupy_grid_same_contract_paths(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("run_rtdl_batched_3d_neighbors", text)
        self.assertIn("run_cupy_grid_3d_ranked_summary", text)
        self.assertIn("ranked-summary-aggregate", text)
        self.assertIn("candidate_count_matches_cupy_grid", text)
        self.assertIn("candidate_count_within_tolerance", text)
        self.assertIn("candidate_count_delta", text)
        self.assertIn("ranked_aggregate_matches_cupy_grid", text)
        self.assertIn("rtdl_beats_cupy_grid_claim_authorized", text)
        self.assertIn("native_engine_customization", text)

    def test_manifest_records_goal2800_live_rtnn_status(self) -> None:
        manifest = rt.v2_5_tiered_benchmark_manifest()
        row = next(app for app in manifest["apps"] if app["app_id"] == "rtnn")

        self.assertEqual(row["tier"], "B")
        self.assertEqual(row["canonical_harness_status"], "ready_with_goal2800_live_ranked_summary_harness")
        self.assertIn("Goal2800", row["pod_evidence_status"])
        self.assertIn("CuPy grid", row["pod_evidence_status"])
        self.assertIn("auto-selection blocked", row["next_action"])
        self.assertEqual(rt.validate_v2_5_tiered_benchmark_manifest()["status"], "accept")

    def test_pod_artifact_records_live_rtnn_parity_without_speedup_claim(self) -> None:
        text = POD_ARTIFACT.read_text(encoding="utf-8")

        self.assertIn('"status": "pass"', text)
        for distribution in ("uniform", "clustered", "shell"):
            self.assertIn(f'"distribution": "{distribution}"', text)
        self.assertIn('"candidate_count_within_tolerance": true', text)
        self.assertIn('"candidate_count_tolerance"', text)
        self.assertIn('"rtdl_beats_cupy_grid_claim_authorized": false', text)
        self.assertIn('"paper_reproduction_claim_authorized": false', text)
        self.assertIn('"native_engine_customization": false', text)

    def test_clean_pod_artifact_records_source_metadata(self) -> None:
        payload = json.loads(CLEAN_POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "pass")
        self.assertRegex(payload["source_commit"], r"^[0-9a-f]{40}$")
        self.assertEqual(payload["source_dirty"], [])
        self.assertIn("NVIDIA", payload["gpu"])
        self.assertEqual(payload["row_count"], 3)
        self.assertTrue(all(row["status"] == "pass" for row in payload["rows"]))

    def test_report_and_consensus_keep_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("RTNN v2.5 Live Ranked-Summary Harness", report)
        self.assertIn("Goal2800", consensus)
        self.assertIn("accept-with-boundary", consensus)
        self.assertIn("same-contract CuPy grid", report)
        self.assertIn("not a speedup claim", report)


if __name__ == "__main__":
    unittest.main()
