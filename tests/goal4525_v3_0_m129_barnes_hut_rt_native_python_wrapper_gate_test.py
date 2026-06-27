from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4525_v3_0_m129_barnes_hut_rt_native_python_wrapper_gate_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4525_v3_0_m129_barnes_hut_rt_native_python_wrapper_gate_2026-06-17.md"
README = ROOT / "examples/benchmark_apps/barnes_hut/README.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
SCRIPT = ROOT / "scripts/goal4525_m129_barnes_hut_rt_native_python_wrapper_gate.py"


class Goal4525V30M129BarnesHutRtNativePythonWrapperGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module(
            "scripts.goal4525_m129_barnes_hut_rt_native_python_wrapper_gate"
        )
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_wrapper_surface_is_exported_but_native_execution_remains_blocked(self) -> None:
        packet = self.packet
        gate = packet["implementation_gate"]

        self.assertEqual(
            "rtdl.v3_0.barnes_hut_rt_native_python_wrapper_gate.goal4525.v1",
            packet["version"],
        )
        self.assertTrue(gate["python_wrapper_ready"])
        self.assertFalse(gate["native_execution_ready"])
        self.assertFalse(gate["native_abi_symbols_ready"])
        self.assertFalse(gate["optix_traversal_proof_ready"])
        self.assertIn(gate["status"], {"blocked_missing_native_symbols", "blocked_fail_closed_native_scaffold"})
        self.assertTrue(
            set(packet["native_audit"]["missing_native_symbols"]).issubset(
                set(rt.AGGREGATE_TREE_FUSED_WEIGHTED_VECTOR_SUM_2D_RT_NATIVE_REQUIRED_SYMBOLS)
            )
        )
        self.assertTrue(hasattr(rt, "prepare_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_optix"))
        self.assertTrue(hasattr(rt, "PreparedOptixAggregateTreeFusedWeightedVectorSum2D"))
        self.assertTrue(hasattr(rt, "OptixAggregateTreeFusedWeightedVectorSum2DOutput"))

    def test_output_wrapper_reports_exact_contract_columns_without_claims(self) -> None:
        output = rt.OptixAggregateTreeFusedWeightedVectorSum2DOutput(
            library=object(),
            prepared_owner=object(),
            source_ids_device_ptr=1,
            vector_x_device_ptr=2,
            vector_y_device_ptr=3,
            visited_counts_device_ptr=4,
            aggregate_counts_device_ptr=5,
            exact_counts_device_ptr=6,
            source_count=2,
            diagnostic_status_code=0,
            overflow=False,
            device_ordinal=0,
            bvh_build_seconds=0.1,
            traversal_seconds=0.2,
            continuation_seconds=0.0,
            copy_seconds=0.0,
        )
        metadata = output.to_metadata()

        self.assertTrue(output.device_resident)
        self.assertEqual(
            rt.AGGREGATE_TREE_FUSED_WEIGHTED_VECTOR_SUM_2D_OUTPUT_COLUMNS,
            output.output_columns,
        )
        self.assertEqual(rt.AGGREGATE_TREE_FUSED_WEIGHTED_VECTOR_SUM_2D_RT_NATIVE_CONTRACT, metadata["contract"])
        self.assertFalse(metadata["frontier_rows_emitted"])
        self.assertFalse(metadata["frontier_rows_materialized_on_host"])
        self.assertFalse(metadata["contribution_rows_materialized_on_host"])
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])

    def test_queue_report_docs_and_boundary_are_updated(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")
        queue = self.packet["queue_alignment"]
        boundary = self.packet["claim_boundary"]

        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertEqual("closed_current_target", queue["barnes_hut_work_class"])
        self.assertIsNone(queue["barnes_hut_priority"])
        self.assertIn("Goal4525", queue["barnes_hut_evidence_refs"])
        self.assertIn("subtree-skip semantics", queue["barnes_hut_remaining_gap"])
        self.assertIn("Goal4525 / V3 M129", report)
        self.assertIn("Goal4525", readme)
        self.assertIn("Goal4525 Barnes-Hut RT-native Python wrapper gate", index)
        self.assertIn("wrapper_checks", script)
        self.assertFalse(boundary["runtime_executed"])
        self.assertFalse(boundary["current_route_changed"])
        self.assertFalse(boundary["rt_core_speedup_claim_authorized"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
