from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal2802_rt_dbscan_v25_live_grouped_stream_harness.py"
REPORT = ROOT / "docs" / "reports" / "goal2802_rt_dbscan_v2_5_live_grouped_stream_harness_2026-05-31.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal2802_rt_dbscan_v2_5_live_grouped_stream_harness_consensus_2026-05-31.md"
POD_ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2802_pod_artifacts"
    / "rt_dbscan_v25_live_grouped_stream_32768_65536_131072.json"
)
CLEAN_POD_ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2802_pod_artifacts"
    / "rt_dbscan_v25_live_grouped_stream_32768_65536_131072_clean_from_git.json"
)


class Goal2802RTDBSCANV25LiveGroupedStreamHarnessTest(unittest.TestCase):
    def test_entrypoint_records_current_grouped_stream_contract(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("run_goal2802_rt_dbscan_live_harness", text)
        self.assertIn("PREPARED_CUPY_GRID_MODE", text)
        self.assertIn("PREPARED_GRID_MODE", text)
        self.assertIn("grouped_stream_avoids_neighbor_rows_and_full_adjacency_stream", text)
        self.assertIn("native_engine_customization", text)

    def test_manifest_records_goal2802_rt_dbscan_status(self) -> None:
        manifest = rt.v2_5_tiered_benchmark_manifest()
        row = next(app for app in manifest["apps"] if app["app_id"] == "rt_dbscan")

        self.assertEqual(row["tier"], "B")
        self.assertEqual(row["canonical_harness_status"], "ready_with_goal2802_live_grouped_stream_harness")
        self.assertIn("Goal2802", row["pod_evidence_status"])
        self.assertIn("grouped-stream", row["pod_evidence_status"])
        self.assertIn("auto-selection blocked", row["next_action"])
        self.assertEqual(rt.validate_v2_5_tiered_benchmark_manifest()["status"], "accept")

    def test_pod_artifact_records_signature_match_and_claim_boundary(self) -> None:
        text = POD_ARTIFACT.read_text(encoding="utf-8")
        clean_text = CLEAN_POD_ARTIFACT.read_text(encoding="utf-8")

        for artifact_text in (text, clean_text):
            self.assertIn('"status": "pass"', artifact_text)
            self.assertIn('"signatures_match": true', artifact_text)
            self.assertIn('"grouped_stream_rt_core_accelerated": true', artifact_text)
            self.assertIn('"grouped_stream_avoids_neighbor_rows_and_full_adjacency_stream": true', artifact_text)
            self.assertIn('"paper_speedup_claim_authorized": false', artifact_text)
            self.assertIn('"native_engine_customization": false', artifact_text)

    def test_clean_pod_artifact_records_source_metadata(self) -> None:
        payload = json.loads(CLEAN_POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "pass")
        self.assertRegex(payload["source_commit"], r"^[0-9a-f]{40}$")
        self.assertEqual(payload["source_dirty"], [])
        self.assertIn("NVIDIA", payload["gpu"])
        self.assertTrue(payload["signatures_match"])
        self.assertTrue(payload["grouped_stream_rt_core_accelerated"])
        self.assertTrue(payload["grouped_stream_avoids_neighbor_rows_and_full_adjacency_stream"])

    def test_report_and_consensus_keep_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("RT-DBSCAN v2.5 Live Grouped-Stream Harness", report)
        self.assertIn("Goal2802", consensus)
        self.assertIn("accept-with-boundary", consensus)
        self.assertIn("not a paper-reproduction claim", report)
        self.assertIn("CuPy prepared-grid", report)
        self.assertIn("clean-from-Git pod validated", report)
        self.assertIn("676844e4dc9d0883984827a2b6241781167020ef", consensus)


if __name__ == "__main__":
    unittest.main()
