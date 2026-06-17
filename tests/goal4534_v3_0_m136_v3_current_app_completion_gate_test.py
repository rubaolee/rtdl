from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4534_v3_0_m136_v3_current_app_completion_gate_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4534_v3_0_m136_v3_current_app_completion_gate_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4534V30M136CurrentAppCompletionGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4534_m136_v3_current_app_completion_gate")
        cls.packet = cls.module.build_packet()
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_packet_checks_all_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.current_app_completion_gate.goal4534.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        self.assertEqual("accept", rt.validate_v3_benchmark_implementation_queue()["status"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_all_current_blocker_queues_are_empty(self) -> None:
        summary = self.packet["summary"]
        self.assertEqual((), tuple(summary["runtime_build_queue"]))
        self.assertEqual((), tuple(summary["claim_or_evidence_queue"]))
        self.assertEqual((), tuple(summary["design_blocker_queue"]))
        self.assertEqual(
            ("barnes_hut", "triangle_counting"),
            tuple(summary["future_design_target_queue"]),
        )
        self.assertEqual(8, len(summary["closed_current_targets"]))

    def test_future_design_targets_do_not_authorize_claims(self) -> None:
        future = self.packet["future_design_targets"]
        for app in ("barnes_hut", "triangle_counting"):
            row = future[app]
            self.assertEqual("future_design_target", row["work_class"])
            self.assertIn("no current V3 app implementation blocker", row["remaining_gap"])
            self.assertFalse(row["public_speedup_claim_authorized"])
            self.assertFalse(row["broad_rt_core_claim_authorized"])
            self.assertFalse(row["paper_reproduction_claim_authorized"])
            self.assertFalse(row["automatic_partner_selection_authorized"])
            self.assertFalse(row["app_specific_native_engine_logic_allowed"])
        self.assertIn("hierarchical traversal", future["barnes_hut"]["next_build_target"])
        self.assertIn("capture-compatible OptiX", future["triangle_counting"]["next_build_target"])

    def test_report_index_and_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        boundary = self.packet["claim_boundary"]

        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4534 / V3 M136", report)
        self.assertIn("Goal4534 V3 current app completion gate", index)
        self.assertFalse(boundary["runtime_executed"])
        self.assertFalse(boundary["current_route_changed"])
        self.assertFalse(boundary["release_authorized"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])
        self.assertFalse(boundary["broad_rt_core_claim_authorized"])
        self.assertFalse(boundary["paper_reproduction_claim_authorized"])
        self.assertFalse(boundary["automatic_partner_selection_authorized"])
        self.assertFalse(boundary["app_specific_native_engine_logic_allowed"])


if __name__ == "__main__":
    unittest.main()
