from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2969_current_head_packet_and_10_app_triage_2026-06-01.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2969_current_head_packet_pod"
SUMMARY = ARTIFACT_DIR / "goal2855_summary.json"
TRIAGE = ARTIFACT_DIR / "goal2969_triage.json"
EXPECTED_COMMIT = "deb8369056009cde7c8027f97b45fffbb01729da"


class Goal2969CurrentHeadPacketAnd10AppTriageTest(unittest.TestCase):
    def test_current_head_packet_passes_cleanly(self) -> None:
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

        self.assertEqual("pass", summary["status"])
        self.assertTrue(summary["all_pass"])
        self.assertEqual(EXPECTED_COMMIT, summary["source_commit"])
        self.assertEqual(7, summary["artifact_count"])
        self.assertEqual({}, summary["claim_boundary_violations"])
        self.assertEqual({}, summary["dirty_artifacts"])
        for artifact in summary["artifacts"].values():
            with self.subTest(app=artifact["app"]):
                self.assertEqual("pass", artifact["status"])
                self.assertEqual(EXPECTED_COMMIT, artifact["source_commit"])
                self.assertEqual([], artifact["source_dirty"])

    def test_current_head_triage_indexes_10_apps_and_zero_targets(self) -> None:
        triage = json.loads(TRIAGE.read_text(encoding="utf-8"))

        self.assertEqual("pass", triage["status"])
        self.assertEqual(10, len(triage["apps"]))
        self.assertEqual([], triage["performance_targets"])
        self.assertIsNone(triage["top_priority"])
        self.assertEqual({}, triage["claim_boundary_violations"])
        raydb = triage["apps"][0]
        self.assertEqual("raydb_style", raydb["app"])
        self.assertEqual("pass", raydb["status"])
        self.assertGreaterEqual(float(raydb["min_hit_stream_triton_slowdown_vs_primitive_first"]), 30.0)

    def test_readiness_uses_current_head_packet_and_triage(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertEqual("accept", validation["status"])
        self.assertIn("goal2969_current_head_packet_pod", packet["current_canonical_runner"]["summary_path"])
        self.assertIn("goal2969_triage", packet["current_packet_perf_triage"]["path"])
        self.assertEqual(EXPECTED_COMMIT, packet["current_canonical_runner"]["source_commit"])
        self.assertEqual(0, packet["current_packet_perf_triage"]["performance_target_count"])
        self.assertFalse(packet["claim_authorization"]["v2_5_release_authorized"])

    def test_report_documents_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2969",
            "Source commit: `deb8369056009cde7c8027f97b45fffbb01729da`",
            "Performance targets | `0`",
            "`161.735x`",
            "does not authorize",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
