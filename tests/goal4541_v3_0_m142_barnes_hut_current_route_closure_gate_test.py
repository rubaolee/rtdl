from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = (
    ROOT
    / "docs/reports/goal4541_v3_0_m142_barnes_hut_current_route_closure_gate_2026-06-17.json"
)
REPORT = (
    ROOT
    / "docs/reports/goal4541_v3_0_m142_barnes_hut_current_route_closure_gate_2026-06-17.md"
)
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
README = ROOT / "examples/current/research_benchmarks/barnes_hut/README.md"


class Goal4541V30M142BarnesHutCurrentRouteClosureGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module(
            "scripts.goal4541_m142_barnes_hut_current_route_closure_gate"
        )
        cls.packet = cls.module.build_packet()
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_closure_gate_checks_all_pass(self) -> None:
        self.assertEqual(
            "rtdl.v3_0.barnes_hut_current_route_closure_gate.goal4541.v1",
            self.packet["version"],
        )
        self.assertEqual((), self.packet["failed_checks"])
        self.assertEqual("accept", rt.validate_v3_benchmark_implementation_queue()["status"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_barnes_hut_is_closed_without_rt_native_claim(self) -> None:
        row = self.packet["barnes_hut_row"]
        boundary = self.packet["claim_boundary"]
        self.assertEqual("closed_current_target", row["work_class"])
        self.assertIsNone(row["priority"])
        self.assertFalse(row["pod_needed_next"])
        self.assertIn("Goal4512", row["evidence_refs"])
        self.assertIn("Goal4527", row["evidence_refs"])
        self.assertIn("Goal4541", row["evidence_refs"])
        self.assertIn("RT-native", row["remaining_gap"])
        self.assertIn("hierarchical traversal", row["remaining_gap"])
        self.assertFalse(boundary["rt_native_hierarchical_traversal_implemented"])
        self.assertFalse(boundary["rt_core_speedup_claim_authorized"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])
        self.assertFalse(boundary["automatic_partner_selection_authorized"])
        self.assertFalse(boundary["app_specific_native_engine_logic_allowed"])

    def test_all_current_apps_are_now_closed(self) -> None:
        summary = self.packet["summary"]
        self.assertEqual((), tuple(summary["runtime_build_queue"]))
        self.assertEqual((), tuple(summary["claim_or_evidence_queue"]))
        self.assertEqual((), tuple(summary["design_blocker_queue"]))
        self.assertEqual((), tuple(summary["future_design_target_queue"]))
        self.assertEqual(10, len(summary["closed_current_targets"]))
        self.assertIn("barnes_hut", summary["closed_current_targets"])

    def test_route_adequacy_report_and_docs_are_wired(self) -> None:
        route = self.packet["barnes_hut_route_decision"]
        adequacy = self.packet["barnes_hut_adequacy"]
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4541", route["evidence_refs"])
        self.assertIn("Goal4541", adequacy["evidence_refs"])
        self.assertFalse(route["pod_needed_next"])
        self.assertFalse(adequacy["pod_needed_next"])
        self.assertIn("Goal4541 / V3 M142", report)
        self.assertIn("Goal4541 Barnes-Hut current route closure gate", index)
        self.assertIn("Goal4541", readme)


if __name__ == "__main__":
    unittest.main()
