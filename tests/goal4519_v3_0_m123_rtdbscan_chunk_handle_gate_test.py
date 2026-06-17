from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4519_v3_0_m123_rtdbscan_chunk_handle_gate_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4519_v3_0_m123_rtdbscan_chunk_handle_gate_2026-06-17.md"
README = ROOT / "examples/current/research_benchmarks/rt_dbscan/README.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
SCRIPT = ROOT / "scripts/goal4519_m123_rtdbscan_chunk_handle_gate.py"
SOURCE = ROOT / "src/rtdsl/v3_0_prepared_graph_chunk_executor.py"
INIT = ROOT / "src/rtdsl/__init__.py"


class Goal4519V30M123RtDbscanChunkHandleGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))
        cls.readiness = cls.packet["readiness"]
        cls.validation = cls.packet["validation"]

    def test_generic_chunk_local_handle_gate_blocks_without_smoke_and_graph_capture(self) -> None:
        self.assertEqual("rtdl.v3_0.rtdbscan_chunk_handle_gate.goal4519.v1", self.packet["version"])
        self.assertEqual(rt.V3_CHUNK_LOCAL_PREPARED_HANDLE_GATE_VERSION, self.readiness["version"])
        self.assertEqual("accept", self.validation["status"])
        self.assertTrue(self.readiness["api_shape_ready"])
        self.assertFalse(self.readiness["ready_for_m113_plan"])
        self.assertEqual(
            (
                "live_chunk_handle_smoke_not_validated",
                "prepared_graph_capture_not_validated",
            ),
            tuple(self.validation["blockers"]),
        )
        self.assertFalse(self.readiness["runtime_executed"])
        self.assertFalse(self.readiness["automatic_partner_selection_authorized"])
        self.assertFalse(self.readiness["public_speedup_claim_authorized"])

    def test_gate_can_be_ready_when_all_runtime_requirements_are_proven(self) -> None:
        ready = rt.assess_v3_chunk_local_prepared_handle_readiness(
            app_id="rt_dbscan",
            contract_key="fixed_radius_compact_status_continuation_v1",
            operation="prepared_graph_partner_continuation",
            item_count=2_000_000,
            max_item_count=65_536,
            whole_dataset_prepared_handle_available=True,
            caller_owned_item_columns_available=True,
            chunk_slice_prepare_api_available=True,
            live_chunk_handle_smoke_validated=True,
            prepared_graph_capture_validated=True,
            partner_continuation_explicit=True,
            partner_continuation_associative=True,
            host_materialization_before_partner=False,
        )
        validation = rt.validate_v3_chunk_local_prepared_handle_readiness(ready)
        self.assertTrue(ready["ready_for_m113_plan"])
        self.assertEqual(31, validation["chunk_count"])
        self.assertEqual("chunked_partner_continuation_required", validation["plan_status"])

    def test_source_api_shape_and_exports_are_present(self) -> None:
        audit = self.packet["source_audit"]
        source = SOURCE.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")

        self.assertTrue(audit["whole_dataset_prepared_handle_api_present"])
        self.assertTrue(audit["caller_owned_point_columns_prepare_api_present"])
        self.assertTrue(audit["prepared_predicate_direct_status_handle_class_present"])
        self.assertTrue(audit["runtime_columns_reused"])
        self.assertTrue(audit["pair_materialization_avoided"])
        self.assertFalse(audit["graph_capture_api_present"])
        self.assertIn("assess_v3_chunk_local_prepared_handle_readiness", source)
        self.assertIn("validate_v3_chunk_local_prepared_handle_readiness", source)
        self.assertIn("V3_CHUNK_LOCAL_PREPARED_HANDLE_GATE_VERSION", init)

    def test_report_readme_index_and_script_capture_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("Goal4519 / V3 M123", report)
        self.assertIn("Ready for M113 plan: `False`", report)
        self.assertIn("Goal4519", readme)
        self.assertIn("chunk-handle smoke", readme)
        self.assertIn("Goal4519 RT-DBSCAN chunk-handle gate", index)
        self.assertIn("PACKET_VERSION", script)
        self.assertFalse(self.packet["claim_boundary"]["current_route_changed"])
        self.assertFalse(self.packet["claim_boundary"]["m113_promotion_authorized"])


if __name__ == "__main__":
    unittest.main()
