from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4540_v3_0_m141_triangle_non_graph_stream_closure_gate_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4540_v3_0_m141_triangle_non_graph_stream_closure_gate_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4540V30M141TriangleNonGraphStreamClosureGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module(
            "scripts.goal4540_m141_triangle_non_graph_stream_closure_gate"
        )
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_successor_gate_checks_all_pass(self) -> None:
        self.assertEqual(
            "rtdl.v3_0.triangle_non_graph_stream_closure_gate.goal4540.v1",
            self.packet["version"],
        )
        self.assertEqual((), self.packet["failed_checks"])
        self.assertEqual("accept", rt.validate_v3_benchmark_implementation_queue()["status"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_triangle_is_closed_without_graph_or_public_claims(self) -> None:
        triangle = self.packet["triangle_row"]
        boundary = self.packet["claim_boundary"]
        self.assertEqual("closed_current_target", triangle["work_class"])
        self.assertIsNone(triangle["priority"])
        self.assertIn("Goal4540", triangle["evidence_refs"])
        self.assertTrue(boundary["queue_reclassification_authorized"])
        self.assertTrue(boundary["prepared_weighted_replay_device_output_stream_validated"])
        self.assertFalse(boundary["prepared_weighted_replay_graph_capture_validated"])
        self.assertFalse(boundary["m113_promotion_authorized_for_future_triangle_shape"])
        self.assertFalse(boundary["m113_replaces_current_triangle_route"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])
        self.assertFalse(boundary["broad_rt_core_claim_authorized"])
        self.assertFalse(boundary["automatic_partner_selection_authorized"])
        self.assertFalse(boundary["app_specific_native_engine_logic_allowed"])

    def test_barnes_hut_is_closed_by_successor_gate(self) -> None:
        summary = self.packet["summary"]
        self.assertEqual((), tuple(summary["future_design_target_queue"]))
        self.assertEqual(10, len(summary["closed_current_targets"]))
        self.assertIn("triangle_counting", summary["closed_current_targets"])
        self.assertIn("barnes_hut", summary["closed_current_targets"])
        self.assertEqual("closed_current_target", self.packet["barnes_hut_row"]["work_class"])
        self.assertIn("Goal4541", self.packet["barnes_hut_row"]["evidence_refs"])

    def test_goal4539_evidence_and_review_caveat_are_recorded(self) -> None:
        runtime = self.packet["goal4539_runtime"]
        review = self.packet["review_intake"]
        self.assertTrue(runtime["device_output_stream_prelaunch_validated"])
        self.assertEqual((), tuple(runtime["graph_capture_validated_modes"]))
        self.assertTrue(runtime["graph_capture_mode_independent_reject"])
        self.assertEqual("request_changes_for_goal4539_direct_flip", review["singer_verdict"])
        self.assertEqual("approve_with_caveats", review["ramanujan_verdict"])
        self.assertIn("M113 graph readiness", review["shared_caveat"])

    def test_report_index_and_checked_in_packet_are_wired(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4540 / V3 M141", report)
        self.assertIn("Triangle queue reclassification is authorized only", report)
        self.assertIn("Goal4540 Triangle non-graph stream closure gate", index)


if __name__ == "__main__":
    unittest.main()
