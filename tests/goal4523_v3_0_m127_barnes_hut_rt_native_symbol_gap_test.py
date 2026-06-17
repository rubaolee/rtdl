from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4523_v3_0_m127_barnes_hut_rt_native_symbol_gap_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4523_v3_0_m127_barnes_hut_rt_native_symbol_gap_2026-06-17.md"
README = ROOT / "examples/current/research_benchmarks/barnes_hut/README.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
SCRIPT = ROOT / "scripts/goal4523_m127_barnes_hut_rt_native_symbol_gap.py"


class Goal4523V30M127BarnesHutRtNativeSymbolGapTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_required_fused_rt_native_symbols_are_still_missing(self) -> None:
        packet = self.packet
        self.assertEqual("rtdl.v3_0.barnes_hut_rt_native_symbol_gap.goal4523.v1", packet["version"])
        self.assertEqual("blocked_missing_native_symbols", packet["implementation_gate"]["status"])
        self.assertEqual(
            list(rt.AGGREGATE_TREE_FUSED_WEIGHTED_VECTOR_SUM_2D_RT_NATIVE_REQUIRED_SYMBOLS),
            packet["source_audit"]["missing_native_symbols"],
        )
        self.assertEqual(
            packet["source_audit"]["missing_native_symbols"],
            packet["source_audit"]["missing_python_wrappers"],
        )
        for symbol, check in packet["source_audit"]["symbol_checks"].items():
            self.assertFalse(check["native_present_anywhere"], symbol)
            self.assertFalse(check["python_wrapper_present"], symbol)
            self.assertTrue(all(value is False for value in check["native_occurrences"].values()))

    def test_gap_distinguishes_generic_optix_machinery_from_fused_contract(self) -> None:
        audit = self.packet["source_audit"]
        gate = self.packet["implementation_gate"]
        self.assertTrue(audit["generic_optix_traversal_available_elsewhere"])
        self.assertFalse(audit["fused_rt_native_block_present"])
        self.assertFalse(gate["native_abi_symbols_ready"])
        self.assertFalse(gate["python_wrapper_ready"])
        self.assertFalse(gate["optix_traversal_proof_ready"])
        self.assertFalse(gate["equivalence_oracle_ready"])
        self.assertFalse(gate["timing_split_ready"])

    def test_report_docs_and_boundary_are_present(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")
        boundary = self.packet["claim_boundary"]

        self.assertIn("Goal4523 / V3 M127", report)
        self.assertIn("Missing Symbols", report)
        self.assertIn("src/native/optix/rtdl_optix_core.cpp", report)
        self.assertIn("Goal4523", readme)
        self.assertIn("Goal4523 Barnes-Hut RT-native symbol gap", index)
        self.assertIn("NATIVE_PATHS", script)
        self.assertFalse(boundary["runtime_executed"])
        self.assertFalse(boundary["current_route_changed"])
        self.assertFalse(boundary["rt_core_speedup_claim_authorized"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
