from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt
from rtdsl.v3_0_execution_graph import GraphValidationError


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4509_v3_0_m113_prepared_graph_chunk_executor_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4509_v3_0_m113_prepared_graph_chunk_executor_2026-06-17.md"
README = ROOT / "examples/benchmark_apps/rtnn/README.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4509V30M113PreparedGraphChunkExecutorTest(unittest.TestCase):
    def test_generic_chunk_executor_plans_and_validates_large_explicit_continuation(self) -> None:
        plan = rt.plan_v3_prepared_graph_chunk_executor(
            graph_id="prepared_graph_chunk_executor_reference",
            contract_key="prepared_graph_chunk_executor_contract_v1",
            operation="prepared_graph_partner_continuation",
            item_count=1_048_576,
            max_item_count=65_536,
        )
        validation = rt.validate_v3_prepared_graph_chunk_executor_plan(plan)

        self.assertEqual(rt.V3_PREPARED_GRAPH_CHUNK_EXECUTOR_VERSION, plan["version"])
        self.assertEqual(rt.V3_PREPARED_GRAPH_CHUNK_EXECUTOR_STATUS, plan["status"])
        self.assertEqual("accept", validation["status"])
        self.assertEqual(16, plan["chunk_count"])
        self.assertTrue(plan["single_graph_cap_exceeded"])
        self.assertEqual(0, plan["chunks"][0]["item_start_inclusive"])
        self.assertEqual(1_048_576, plan["chunks"][-1]["item_end_exclusive"])
        for chunk in plan["chunks"]:
            self.assertTrue(chunk["prepared_scene_reused"])
            self.assertTrue(chunk["prepared_item_handle_per_chunk"])
            self.assertTrue(chunk["prepared_graph_per_chunk"])
            self.assertTrue(chunk["partner_continuation_per_chunk"])
            self.assertFalse(chunk["host_materialization_before_partner"])
        self.assertFalse(plan["aggregate_only_substitute_allowed"])
        self.assertFalse(plan["hidden_auto_dispatch_allowed"])
        self.assertFalse(plan["automatic_partner_selection_authorized"])

    def test_generic_chunk_executor_rejects_non_continuation_and_public_claims(self) -> None:
        with self.assertRaisesRegex(GraphValidationError, "partner continuation"):
            rt.plan_v3_prepared_graph_chunk_executor(
                graph_id="prepared_graph_chunk_executor_reference",
                contract_key="prepared_graph_chunk_executor_contract_v1",
                operation="prepared_graph_partner_continuation",
                item_count=4,
                max_item_count=2,
                requires_partner_continuation=False,
            )

        plan = rt.plan_v3_prepared_graph_chunk_executor(
            graph_id="prepared_graph_chunk_executor_reference",
            contract_key="prepared_graph_chunk_executor_contract_v1",
            operation="prepared_graph_partner_continuation",
            item_count=4,
            max_item_count=2,
        )
        broken = dict(plan)
        broken["public_speedup_claim_authorized"] = True
        with self.assertRaisesRegex(GraphValidationError, "public_speedup"):
            rt.validate_v3_prepared_graph_chunk_executor_plan(broken)

    def test_m19_plan_reuses_generic_executor_without_losing_legacy_query_fields(self) -> None:
        plan = rt.plan_v3_m19_ranked_summary_bridge_chunks(
            point_count=1_048_576,
            query_count=1_048_576,
            distribution="uniform",
        )
        nested = plan["prepared_graph_chunk_executor_plan"]

        self.assertEqual(rt.V3_M19_CHUNK_PLAN_VERSION, plan["version"])
        self.assertEqual(rt.V3_PREPARED_GRAPH_CHUNK_EXECUTOR_VERSION, nested["version"])
        self.assertEqual(plan["query_count"], nested["item_count"])
        self.assertEqual(plan["chunk_count"], nested["chunk_count"])
        self.assertIn("query_start_inclusive", plan["chunks"][0])
        self.assertIn("item_start_inclusive", nested["chunks"][0])
        self.assertEqual("accept", rt.validate_v3_m19_ranked_summary_bridge_chunk_plan(plan)["status"])

        broken_nested = dict(nested)
        broken_nested["item_count"] = 1
        broken = dict(plan)
        broken["prepared_graph_chunk_executor_plan"] = broken_nested
        with self.assertRaisesRegex(GraphValidationError, "item_count"):
            rt.validate_v3_m19_ranked_summary_bridge_chunk_plan(broken)

    def test_signature_combiner_is_app_agnostic(self) -> None:
        combined = rt.combine_v3_prepared_graph_chunk_signatures(
            (
                ((1, 2, 3), (4, 5, 6)),
                ((10, 20, 30), (40, 50, 60)),
            )
        )
        self.assertEqual(((11, 22, 33), (44, 55, 66)), combined)

        with self.assertRaisesRegex(GraphValidationError, "inconsistent width"):
            rt.combine_v3_prepared_graph_chunk_signatures((((1, 2),), ((1, 2, 3),)))

    def test_packet_report_and_docs_capture_m113_boundary(self) -> None:
        module = importlib.import_module("scripts.goal4509_m113_prepared_graph_chunk_executor")
        packet = module.build_packet(ROOT)
        checked_in = json.loads(PACKET.read_text(encoding="utf-8"))
        report = REPORT.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")

        self.assertEqual("rtdl.v3_0.prepared_graph_chunk_executor.goal4509.v1", packet["version"])
        self.assertEqual(16, packet["large_chunk_plan"]["chunk_count"])
        self.assertTrue(packet["claim_boundary"]["app_agnostic_contract_ready"])
        self.assertTrue(packet["claim_boundary"]["m19_reuses_generic_plan"])
        self.assertFalse(packet["claim_boundary"]["runtime_executed"])
        self.assertFalse(packet["claim_boundary"]["automatic_partner_selection_authorized"])
        self.assertEqual(packet["version"], checked_in["version"])
        self.assertIn("app-agnostic prepared graph chunk executor", report)
        self.assertIn("not new runtime performance evidence", report)
        self.assertIn("plan_v3_prepared_graph_chunk_executor", readme)
        self.assertIn("Goal4509 prepared graph chunk executor", index)


if __name__ == "__main__":
    unittest.main()
