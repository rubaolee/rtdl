from __future__ import annotations

import importlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

import rtdsl as rt
from examples.benchmark_apps.rtnn import rtdl_rtnn_benchmark_app as app
from rtdsl.v3_0_execution_graph import GraphValidationError


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples/benchmark_apps/rtnn/rtdl_rtnn_benchmark_app.py"
PACKET = ROOT / "docs/reports/goal4505_v3_0_m109_rtnn_partner_chunk_plan_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4505_v3_0_m109_rtnn_partner_chunk_plan_2026-06-17.md"
SCRIPT = ROOT / "scripts/goal4505_m109_rtnn_partner_chunk_plan.py"
README = ROOT / "examples/benchmark_apps/rtnn/README.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4505V30M109RtnnPartnerChunkPlanTest(unittest.TestCase):
    def test_m19_planner_chunks_large_partner_continuation(self) -> None:
        plan = rt.plan_v3_m19_ranked_summary_bridge_chunks(
            point_count=1_048_576,
            query_count=1_048_576,
            distribution="uniform",
        )
        validation = rt.validate_v3_m19_ranked_summary_bridge_chunk_plan(plan)

        self.assertEqual("accept", validation["status"])
        self.assertEqual(rt.V3_M19_CHUNK_PLAN_VERSION, plan["version"])
        self.assertEqual(65_536, plan["max_query_count"])
        self.assertEqual(16, plan["chunk_count"])
        self.assertTrue(plan["single_graph_cap_exceeded"])
        self.assertEqual("chunked_partner_continuation_required", plan["plan_status"])
        self.assertFalse(plan["aggregate_only_full_batch_direct_substitute_allowed"])
        self.assertFalse(plan["hidden_auto_dispatch_allowed"])
        self.assertFalse(plan["public_speedup_claim_authorized"])
        self.assertEqual(0, plan["chunks"][0]["query_start_inclusive"])
        self.assertEqual(1_048_576, plan["chunks"][-1]["query_end_exclusive"])
        for chunk in plan["chunks"]:
            self.assertLessEqual(chunk["query_count"], 65_536)
            self.assertTrue(chunk["prepared_scene_reused"])
            self.assertTrue(chunk["prepared_query_points_per_chunk"])
            self.assertTrue(chunk["cuda_graph_per_chunk"])
            self.assertTrue(chunk["same_stream_partner_device_reduction_per_chunk"])
            self.assertFalse(chunk["host_materialization_before_partner"])

    def test_m19_runtime_rejects_large_query_with_planner_guidance(self) -> None:
        with self.assertRaisesRegex(GraphValidationError, "plan_v3_m19_ranked_summary_bridge_chunks"):
            rt.run_v3_m19_ranked_summary_bridge_case(
                transfer_counter_library="build/fake_counter.so",
                point_count=65_537,
                query_count=65_537,
                warmups=0,
                repeats=1,
            )

    def test_app_exposes_dry_run_chunk_plan_without_transfer_counter(self) -> None:
        payload = app.run_app(
            "prepared_ranked_summary_graph_partner_bridge_plan",
            copies=1_048_576,
            query_count=1_048_576,
            distribution="uniform",
        )
        plan = payload["execution_path_plan"]

        self.assertEqual("prepared_ranked_summary_graph_partner_bridge_plan", payload["mode"])
        self.assertFalse(payload["runtime_executed"])
        self.assertEqual(16, plan["chunk_count"])
        self.assertTrue(payload["claim_boundary"]["large_chunk_runtime_evidence_required"])
        self.assertFalse(payload["claim_boundary"]["aggregate_only_full_batch_direct_substitute_allowed"])
        self.assertEqual("accept", payload["validation"]["status"])

    def test_cli_help_exposes_plan_mode(self) -> None:
        help_text = subprocess.check_output(
            [sys.executable, str(APP), "--help"],
            cwd=ROOT,
            text=True,
        )
        self.assertIn("prepared_ranked_summary_graph_partner_bridge_plan", help_text)

    def test_script_packet_report_and_docs_capture_boundary(self) -> None:
        module = importlib.import_module("scripts.goal4505_m109_rtnn_partner_chunk_plan")
        packet = module.build_packet(ROOT)

        self.assertEqual("rtdl.v3_0.rtnn_partner_chunk_plan.goal4505.v1", packet["version"])
        self.assertEqual(16, packet["large_partner_continuation_plan"]["chunk_count"])
        self.assertFalse(
            packet["large_partner_continuation_plan"][
                "aggregate_only_full_batch_direct_substitute_allowed"
            ]
        )
        self.assertFalse(packet["claim_boundary"]["runtime_executed"])
        self.assertTrue(packet["claim_boundary"]["large_runtime_evidence_required"])

        checked_in = json.loads(PACKET.read_text(encoding="utf-8"))
        report = REPORT.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")

        self.assertEqual("rtdl.v3_0.rtnn_partner_chunk_plan.goal4505.v1", checked_in["version"])
        self.assertIn("16 chunks", report)
        self.assertIn("planner evidence only", report)
        self.assertIn("aggregate-only direct mode is not a substitute", report)
        self.assertIn("prepared_ranked_summary_graph_partner_bridge_plan", script)
        self.assertIn("Goal4505", readme)
        self.assertIn("Goal4505 RTNN partner-continuation chunk plan", index)

    def test_current_route_and_adequacy_include_goal4505_plan_boundary(self) -> None:
        route = rt.explain_current_benchmark_route("rtnn")
        adequacy = {row["app"]: row for row in rt.current_benchmark_adequacy()}["rtnn"]

        self.assertEqual(
            "rtdl.v3_0.current_benchmark_route_decisions.goal4507.v1",
            route["version"],
        )
        self.assertEqual(
            "rtdl.v3_0.current_benchmark_adequacy.goal4507.v1",
            adequacy["version"],
        )
        self.assertIn("Goal4505", route["evidence_refs"])
        self.assertIn("Goal4505", adequacy["evidence_refs"])
        self.assertIn("planner evidence only", route["current_reader_decision"])
        self.assertIn("prepared_ranked_summary_graph_partner_bridge_plan", adequacy["current_recommended_path"])
        self.assertIn(
            "treating the Goal4505 chunk plan as measured large chunked runtime evidence",
            route["rejected_or_unpromoted_candidates"],
        )


if __name__ == "__main__":
    unittest.main()
