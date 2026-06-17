from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4526_v3_0_m130_barnes_hut_rt_native_fail_closed_abi_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4526_v3_0_m130_barnes_hut_rt_native_fail_closed_abi_2026-06-17.md"
README = ROOT / "examples/current/research_benchmarks/barnes_hut/README.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
SCRIPT = ROOT / "scripts/goal4526_m130_barnes_hut_rt_native_fail_closed_abi.py"


class Goal4526V30M130BarnesHutRtNativeFailClosedAbiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module(
            "scripts.goal4526_m130_barnes_hut_rt_native_fail_closed_abi"
        )
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_native_abi_symbols_are_exported_but_execution_is_blocked(self) -> None:
        gate = self.packet["implementation_gate"]
        audit = self.packet["source_audit"]

        self.assertEqual(
            "rtdl.v3_0.barnes_hut_rt_native_fail_closed_abi.goal4526.v1",
            self.packet["version"],
        )
        self.assertTrue(gate["python_wrapper_ready"])
        self.assertTrue(gate["native_abi_symbols_exported"])
        self.assertFalse(gate["native_execution_ready"])
        self.assertFalse(gate["optix_traversal_proof_ready"])
        self.assertFalse(gate["equivalence_oracle_ready"])
        self.assertTrue(audit["output_struct_declared"])
        self.assertTrue(audit["fail_closed_ready"])
        for symbol, check in audit["export_checks"].items():
            self.assertTrue(check["declared_in_prelude"], symbol)
            self.assertTrue(check["defined_in_api"], symbol)
            self.assertTrue(check["python_wrapper_looks_up_symbol"], symbol)

    def test_queue_and_wrapper_gates_reflect_fail_closed_scaffold(self) -> None:
        queue = self.packet["queue_alignment"]
        m129 = importlib.import_module(
            "scripts.goal4525_m129_barnes_hut_rt_native_python_wrapper_gate"
        ).build_packet(ROOT)

        self.assertEqual("closed_current_target", queue["barnes_hut_work_class"])
        self.assertIsNone(queue["barnes_hut_priority"])
        self.assertIn("Goal4526", queue["barnes_hut_evidence_refs"])
        self.assertIn("direct all-node any-hit route", queue["barnes_hut_next_build_target"])
        self.assertEqual("blocked_fail_closed_native_scaffold", m129["implementation_gate"]["status"])
        self.assertTrue(m129["implementation_gate"]["native_abi_symbols_exported"])
        self.assertFalse(m129["implementation_gate"]["native_execution_ready"])

    def test_report_docs_and_boundary_are_present(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")
        boundary = self.packet["claim_boundary"]

        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4526 / V3 M130", report)
        self.assertIn("Goal4526", readme)
        self.assertIn("Goal4526 Barnes-Hut RT-native fail-closed ABI", index)
        self.assertIn("fail_closed_checks", script)
        self.assertFalse(boundary["runtime_executed"])
        self.assertFalse(boundary["current_route_changed"])
        self.assertFalse(boundary["rt_core_speedup_claim_authorized"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
