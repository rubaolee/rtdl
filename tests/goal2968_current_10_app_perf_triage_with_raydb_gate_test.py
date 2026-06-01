from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2968_current_10_app_perf_triage_with_raydb_gate_2026-06-01.md"
TRIAGE = ROOT / "docs" / "reports" / "goal2968_current_packet_plus_raydb_gate_triage_2026-06-01.json"


class Goal2968Current10AppPerfTriageWithRaydbGateTest(unittest.TestCase):
    def test_triage_indexes_all_10_apps_with_raydb_gate_pass(self) -> None:
        payload = json.loads(TRIAGE.read_text(encoding="utf-8"))

        self.assertEqual("pass", payload["status"])
        self.assertEqual(10, len(payload["apps"]))
        self.assertEqual([], payload["performance_targets"])
        self.assertIsNone(payload["top_priority"])
        self.assertEqual({}, payload["claim_boundary_violations"])
        raydb = payload["apps"][0]
        self.assertEqual("raydb_style", raydb["app"])
        self.assertEqual("pass", raydb["status"])
        self.assertEqual("current_path_acceptable", raydb["performance_status"])
        self.assertEqual("primitive_first_fused_grouped_reduction", raydb["route"])
        self.assertGreaterEqual(float(raydb["min_hit_stream_triton_slowdown_vs_primitive_first"]), 30.0)
        self.assertGreater(float(raydb["max_hit_stream_triton_slowdown_vs_primitive_first"]), 100.0)

    def test_readiness_keeps_zero_target_triage_after_goal2968(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertEqual("accept", validation["status"])
        self.assertEqual(0, validation["current_packet_perf_target_count"])
        self.assertEqual(0, packet["current_packet_perf_triage"]["performance_target_count"])
        self.assertFalse(packet["claim_authorization"]["v2_5_release_authorized"])

    def test_report_documents_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2968",
            "10 benchmark apps",
            "`30.138x`",
            "Performance targets | `0`",
            "does not authorize",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
