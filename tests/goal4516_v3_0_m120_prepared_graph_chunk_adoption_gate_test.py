from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt
from rtdsl.v3_0_execution_graph import GraphValidationError


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4516_v3_0_m120_prepared_graph_chunk_adoption_gate_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4516_v3_0_m120_prepared_graph_chunk_adoption_gate_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
SCRIPT = ROOT / "scripts/goal4516_m120_prepared_graph_chunk_adoption_gate.py"


class Goal4516V30M120PreparedGraphChunkAdoptionGateTest(unittest.TestCase):
    def test_core_gate_accepts_ready_explicit_chunked_partner_continuation(self) -> None:
        assessment = rt.assess_v3_prepared_graph_chunk_executor_adoption(
            app_id="rtnn",
            graph_id="prepared_graph_chunk_adoption_gate_reference",
            contract_key="ranked_summary_device_partial_reduction_v1",
            operation="prepared_graph_partner_continuation",
            item_count=1_048_576,
            max_item_count=65_536,
            prepared_scene_reuse_available=True,
            prepared_item_handle_per_chunk_available=True,
            prepared_graph_capture_validated=True,
            partner_continuation_explicit=True,
            partner_continuation_associative=True,
            host_materialization_before_partner=False,
        )
        validation = rt.validate_v3_prepared_graph_chunk_executor_adoption(assessment)

        self.assertEqual(rt.V3_PREPARED_GRAPH_CHUNK_ADOPTION_GATE_VERSION, assessment["version"])
        self.assertEqual(rt.V3_PREPARED_GRAPH_CHUNK_ADOPTION_GATE_STATUS, assessment["status"])
        self.assertTrue(assessment["ready_for_m113_plan"])
        self.assertEqual("ready_for_m113_plan", assessment["adoption_status"])
        self.assertEqual((), assessment["blockers"])
        self.assertIsNotNone(assessment["plan"])
        self.assertEqual(16, assessment["plan"]["chunk_count"])
        self.assertEqual("accept", validation["status"])
        self.assertEqual("chunked_partner_continuation_required", validation["plan_status"])
        self.assertFalse(assessment["automatic_partner_selection_authorized"])
        self.assertFalse(assessment["public_speedup_claim_authorized"])

    def test_core_gate_blocks_missing_graph_and_materialization_debts(self) -> None:
        assessment = rt.assess_v3_prepared_graph_chunk_executor_adoption(
            app_id="barnes_hut",
            graph_id="prepared_graph_chunk_adoption_gate_reference",
            contract_key="aggregate_tree_weighted_vector_sum_v1",
            operation="prepared_graph_partner_continuation",
            item_count=131_072,
            max_item_count=65_536,
            prepared_scene_reuse_available=False,
            prepared_item_handle_per_chunk_available=False,
            prepared_graph_capture_validated=False,
            partner_continuation_explicit=True,
            partner_continuation_associative=True,
            host_materialization_before_partner=True,
        )
        validation = rt.validate_v3_prepared_graph_chunk_executor_adoption(assessment)

        self.assertFalse(assessment["ready_for_m113_plan"])
        self.assertIsNone(assessment["plan"])
        self.assertIn("missing_prepared_scene_reuse", assessment["blockers"])
        self.assertIn("missing_prepared_item_handle_per_chunk", assessment["blockers"])
        self.assertIn("prepared_graph_capture_not_validated", assessment["blockers"])
        self.assertIn("host_materialization_before_partner", assessment["blockers"])
        self.assertEqual("blocked_for_m113_plan", validation["plan_status"])

    def test_core_gate_rejects_claim_or_plan_inconsistency(self) -> None:
        ready = rt.assess_v3_prepared_graph_chunk_executor_adoption(
            app_id="rtnn",
            graph_id="prepared_graph_chunk_adoption_gate_reference",
            contract_key="ranked_summary_device_partial_reduction_v1",
            operation="prepared_graph_partner_continuation",
            item_count=4,
            max_item_count=4,
            prepared_scene_reuse_available=True,
            prepared_item_handle_per_chunk_available=True,
            prepared_graph_capture_validated=True,
            partner_continuation_explicit=True,
            partner_continuation_associative=True,
            host_materialization_before_partner=False,
        )
        broken = dict(ready)
        broken["public_speedup_claim_authorized"] = True
        with self.assertRaisesRegex(GraphValidationError, "public speedup"):
            rt.validate_v3_prepared_graph_chunk_executor_adoption(broken)

        blocked = dict(ready)
        blocked["ready_for_m113_plan"] = False
        blocked["adoption_status"] = "blocked_for_m113_plan"
        blocked["blockers"] = ("prepared_graph_capture_not_validated",)
        with self.assertRaisesRegex(GraphValidationError, "must not include a plan"):
            rt.validate_v3_prepared_graph_chunk_executor_adoption(blocked)

    def test_packet_report_and_index_capture_m120_adoption_gate(self) -> None:
        module = importlib.import_module("scripts.goal4516_m120_prepared_graph_chunk_adoption_gate")
        packet = module.build_packet(ROOT)
        checked_in = json.loads(PACKET.read_text(encoding="utf-8"))
        rows = {row["assessment"]["app_id"]: row for row in packet["rows"]}
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertEqual("rtdl.v3_0.prepared_graph_chunk_adoption_gate.goal4516.v1", packet["version"])
        self.assertEqual(5, packet["summary"]["scenario_count"])
        self.assertEqual(["rtnn"], packet["summary"]["ready_apps"])
        self.assertEqual(
            {"rt_dbscan", "triangle_counting", "spatial_rayjoin", "barnes_hut"},
            set(packet["summary"]["blocked_apps"]),
        )
        self.assertTrue(packet["summary"]["all_validated"])
        self.assertFalse(packet["summary"]["automatic_partner_selection_authorized"])
        self.assertFalse(packet["summary"]["runtime_executed"])
        self.assertEqual("ready_for_m113_plan", rows["rtnn"]["assessment"]["adoption_status"])
        self.assertIn(
            "prepared_graph_capture_not_validated",
            rows["spatial_rayjoin"]["assessment"]["blockers"],
        )
        self.assertIn(
            "partner_continuation_not_associative",
            rows["triangle_counting"]["assessment"]["blockers"],
        )
        self.assertEqual(packet["version"], checked_in["version"])
        self.assertIn("Goal4516 / V3 M120", report)
        self.assertIn("RTNN is ready for M113 planning", report)
        self.assertIn("Goal4516 prepared graph chunk adoption gate", index)
        self.assertIn("assess_v3_prepared_graph_chunk_executor_adoption", script)


if __name__ == "__main__":
    unittest.main()
