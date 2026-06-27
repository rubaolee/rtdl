from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4517_v3_0_m121_aggregate_tree_fused_rt_native_contract_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4517_v3_0_m121_aggregate_tree_fused_rt_native_contract_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
README = ROOT / "examples/benchmark_apps/barnes_hut/README.md"
SOURCE = ROOT / "src/rtdsl/aggregate_tree_reference.py"
INIT = ROOT / "src/rtdsl/__init__.py"
SCRIPT = ROOT / "scripts/goal4517_m121_aggregate_tree_fused_rt_native_contract.py"


class Goal4517V30M121AggregateTreeFusedRtNativeContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))
        cls.contract = cls.packet["contract"]

    def test_contract_surface_is_exported_and_current_runtime_status(self) -> None:
        contract = rt.validate_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_contract()
        self.assertEqual(self.contract["status"], "specified_not_implemented")
        self.assertEqual(
            "generic_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_v1",
            rt.AGGREGATE_TREE_FUSED_WEIGHTED_VECTOR_SUM_2D_RT_NATIVE_CONTRACT,
        )
        self.assertEqual("implemented_cuda_device_accumulation_not_rt_core", contract["status"])
        self.assertTrue(contract["executable"])
        self.assertTrue(contract["app_generic"])
        self.assertEqual("optix", contract["required_first_backend"])
        self.assertIn(
            "vector_x:float64[source_count]",
            contract["output_device_columns"],
        )
        self.assertIn(
            "aggregate-frontier row emission",
            contract["must_avoid"],
        )

    def test_claim_boundary_and_source_evidence_stay_conservative(self) -> None:
        self.assertEqual(
            "rtdl.v3_0.aggregate_tree_fused_rt_native_contract.goal4517.v1",
            self.packet["version"],
        )
        self.assertEqual("contract_specified_runtime_not_implemented", self.packet["status"])
        self.assertTrue(self.packet["source_evidence"]["goal4497_candidate_matches"])
        for key, value in self.packet["claim_boundary"].items():
            self.assertFalse(value, key)
        for key, value in self.contract["claim_boundary"].items():
            self.assertFalse(value, key)
        current_contract = rt.validate_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_contract()
        self.assertTrue(current_contract["claim_boundary"]["runtime_implemented"])
        for key, value in current_contract["claim_boundary"].items():
            if key == "runtime_implemented":
                continue
            self.assertFalse(value, key)
        gate_statuses = {row["gate"]: row["status"] for row in self.packet["implementation_gates"]}
        self.assertEqual("blocked", gate_statuses["native_abi_symbols"])
        self.assertEqual("blocked", gate_statuses["equivalence_oracles"])

    def test_contract_source_avoids_app_specific_native_wording(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")
        block = source[
            source.index("def aggregate_tree_fused_weighted_vector_sum_2d_rt_native_contract") :
            source.index("def validate_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_contract")
        ]
        for phrase in (
            "AGGREGATE_TREE_FUSED_WEIGHTED_VECTOR_SUM_2D_RT_NATIVE_CONTRACT",
            "generic_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_v1",
            "sum_aggregate_frontier_weighted_vectors_2d",
            "sum_aggregate_tree_fused_weighted_vectors_2d_numba_cuda",
            "runtime_implemented",
            "app_specific_native_engine_logic_allowed",
        ):
            self.assertIn(phrase, source)
        for phrase in (
            "aggregate_tree_fused_weighted_vector_sum_2d_rt_native_contract",
            "validate_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_contract",
            "AGGREGATE_TREE_FUSED_WEIGHTED_VECTOR_SUM_2D_RT_NATIVE_CONTRACT",
        ):
            self.assertIn(phrase, init)
        for forbidden in ("Barnes", "barnes", "NBody", "nbody", "n-body", "solver"):
            self.assertNotIn(forbidden, block)

    def test_report_docs_and_index_are_refreshed(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("Goal4517 / V3 M121", report)
        self.assertIn("generic_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_v1", report)
        self.assertIn("Status: depublished for V3 rebuild", index)
        self.assertIn("docs/history/quarantine_v3_v4_reset_2026-06-20", index)
        self.assertIn("Goal4517 specifies the future app-agnostic fused RT-native contract", readme)
        self.assertIn("PACKET_VERSION", script)


if __name__ == "__main__":
    unittest.main()
