from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2959_current_packet_after_rtnn_chunking_2026-06-01.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2959_current_packet_after_rtnn_chunk_pod"
SUMMARY = ARTIFACT_DIR / "goal2855_summary.json"
TRIAGE = ARTIFACT_DIR / "goal2959_triage.json"
EXPECTED_COMMIT = "b4b8d7a6c6554b84870d9a5e67ffd16ebb8b76e8"


class Goal2959CurrentPacketAfterRtnnChunkingTest(unittest.TestCase):
    def test_packet_summary_is_current_clean_and_bounded(self) -> None:
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

        self.assertEqual("pass", summary["status"])
        self.assertEqual(EXPECTED_COMMIT, summary["source_commit"])
        self.assertEqual(7, summary["artifact_count"])
        self.assertEqual({}, summary["claim_boundary_violations"])
        self.assertEqual({}, summary["dirty_artifacts"])
        self.assertFalse(summary["claim_boundary"]["v2_5_release_authorized"])
        for artifact in summary["artifacts"].values():
            self.assertEqual("pass", artifact["status"])
            self.assertEqual(EXPECTED_COMMIT, artifact["source_commit"])
            self.assertEqual([], artifact["source_dirty"])

    def test_triage_stays_zero_target(self) -> None:
        triage = json.loads(TRIAGE.read_text(encoding="utf-8"))

        self.assertEqual("pass", triage["status"])
        self.assertEqual([], triage["performance_targets"])
        self.assertIsNone(triage["top_priority"])
        self.assertEqual(10, len(triage["apps"]))

    def test_readiness_keeps_goal2959_packet_green_after_later_packets(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertEqual("accept", validation["status"])
        self.assertEqual(0, validation["current_packet_perf_target_count"])
        self.assertEqual(0, packet["current_packet_perf_triage"]["performance_target_count"])
        self.assertIn("keep_goal2959_current_packet_after_rtnn_chunking_green", packet["allowed_next_actions"])
        self.assertFalse(packet["claim_authorization"]["v2_5_release_authorized"])

    def test_report_documents_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2959",
            "Performance targets | `0`",
            "`1.145x`",
            "`0.898x`",
            "internal engineering evidence",
            "does not authorize",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
