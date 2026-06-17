from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = (
    ROOT
    / "docs/reports/goal4527_v3_0_m131_barnes_hut_rt_native_traversal_semantic_gate_2026-06-17.json"
)
REPORT = (
    ROOT
    / "docs/reports/goal4527_v3_0_m131_barnes_hut_rt_native_traversal_semantic_gate_2026-06-17.md"
)
README = ROOT / "examples/current/research_benchmarks/barnes_hut/README.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
SCRIPT = ROOT / "scripts/goal4527_m131_barnes_hut_rt_native_traversal_semantic_gate.py"


class Goal4527V30M131BarnesHutRtNativeTraversalSemanticGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module(
            "scripts.goal4527_m131_barnes_hut_rt_native_traversal_semantic_gate"
        )
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_semantic_gate_rejects_naive_all_node_anyhit(self) -> None:
        constraints = self.packet["semantic_constraints"]
        decision = self.packet["implementation_decision"]
        source = self.packet["source_audit"]

        self.assertEqual(
            "rtdl.v3_0.barnes_hut_rt_native_traversal_semantic_gate.goal4527.v1",
            self.packet["version"],
        )
        self.assertTrue(constraints["parent_acceptance_suppresses_descendants"])
        self.assertTrue(constraints["single_custom_primitive_gas_reports_nodes_independently"])
        self.assertFalse(constraints["single_trace_parent_subtree_skip_proof_exists"])
        self.assertFalse(decision["implement_naive_all_node_optix_anyhit"])
        self.assertFalse(decision["replace_fail_closed_abi_now"])
        self.assertTrue(decision["advance_to_rt_dbscan_runtime_work"])
        self.assertTrue(all(source["fail_closed_fragments"].values()))

    def test_queue_advances_to_rt_dbscan_with_barnes_hut_design_blocked(self) -> None:
        queue = self.packet["queue_alignment"]
        checks = queue["queue_checks"]
        validation = rt.validate_v3_benchmark_implementation_queue()

        self.assertEqual("accept", validation["status"])
        self.assertEqual("design_blocker", queue["barnes_hut_work_class"])
        self.assertEqual("rt_dbscan", queue["next_runtime_build_target"])
        self.assertEqual(("rt_dbscan", "triangle_counting"), tuple(queue["runtime_build_queue"]))
        self.assertEqual(("barnes_hut",), tuple(queue["design_blocker_queue"]))
        self.assertTrue(all(checks.values()))

    def test_report_docs_and_boundary_are_present(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")
        boundary = self.packet["claim_boundary"]

        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4527 / V3 M131", report)
        self.assertIn("naive all-node OptiX any-hit", report)
        self.assertIn("Goal4527", readme)
        self.assertIn("Goal4527 Barnes-Hut RT-native traversal semantic gate", index)
        self.assertIn("subtree", script)
        self.assertFalse(boundary["runtime_executed"])
        self.assertFalse(boundary["current_route_changed"])
        self.assertFalse(boundary["rt_core_speedup_claim_authorized"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])
        self.assertFalse(boundary["app_specific_native_engine_logic_allowed"])


if __name__ == "__main__":
    unittest.main()
