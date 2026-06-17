from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4504_v3_0_m108_execution_path_policy_refresh_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4504_v3_0_m108_execution_path_policy_refresh_2026-06-17.md"
SCRIPT = ROOT / "scripts/goal4504_m108_execution_path_policy_refresh.py"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
README = ROOT / "examples/current/research_benchmarks/rtnn/README.md"


class Goal4504V30M108ExecutionPathPolicyRefreshTest(unittest.TestCase):
    def test_script_rebuilds_size_aware_policy_packet(self) -> None:
        module = importlib.import_module("scripts.goal4504_m108_execution_path_policy_refresh")
        packet = module.build_packet(ROOT)
        matrix = packet["scenario_matrix"]

        self.assertEqual("rtdl.v3_0.execution_path_policy_refresh.goal4504.v1", packet["version"])
        self.assertEqual("accept", packet["validation"]["status"])
        self.assertEqual(65_536, packet["graph_query_count_cap"])
        self.assertEqual(
            rt.V2_5_FIXED_RADIUS_AGGREGATE_DIRECT_GRAPH_MODE,
            matrix["unknown_or_small_aggregate_only"]["recommended_result_mode"],
        )
        self.assertEqual(
            rt.V2_5_FIXED_RADIUS_AGGREGATE_FULL_BATCH_DIRECT_MODE,
            matrix["large_aggregate_only_kitti_1m"]["recommended_result_mode"],
        )
        self.assertEqual(
            rt.V2_5_FIXED_RADIUS_AGGREGATE_SAME_STREAM_CUPY_MODE,
            matrix["large_partner_continuation"]["recommended_result_mode"],
        )
        self.assertEqual(
            "backend_specific_policy_required",
            matrix["embree_backend"]["recommended_result_mode"],
        )
        self.assertTrue(
            matrix["large_aggregate_only_kitti_1m"][
                "large_aggregate_only_full_batch_direct_preferred"
            ]
        )
        self.assertFalse(packet["claim_boundary"]["hidden_auto_dispatch_allowed"])
        self.assertFalse(packet["claim_boundary"]["public_speedup_claim_authorized"])

    def test_checked_in_packet_report_and_script_record_goal4502_boundary(self) -> None:
        packet = json.loads(PACKET.read_text(encoding="utf-8"))
        report = REPORT.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        matrix = packet["scenario_matrix"]

        self.assertEqual("rtdl.v3_0.execution_path_policy_refresh.goal4504.v1", packet["version"])
        self.assertEqual("Goal4502", matrix["large_aggregate_only_kitti_1m"]["evidence_goal"])
        self.assertEqual("Goal2841", matrix["unknown_or_small_aggregate_only"]["evidence_goal"])
        self.assertIn("large aggregate-only", report)
        self.assertIn("full-batch prepared direct aggregate", report)
        self.assertIn("same-stream graph/device-partial route", report)
        self.assertIn("hidden runtime dispatch", report)
        self.assertIn("large_partner_continuation", report)
        self.assertIn("query_count=1_000_000", script)
        self.assertIn("Goal4504 RTNN execution-path policy refresh", index)
        self.assertIn("size-aware execution-path policy", readme)
        self.assertIn("Goal4504 codifies", readme)

    def test_current_route_and_adequacy_include_goal4504_policy(self) -> None:
        route = rt.explain_current_benchmark_route("rtnn")
        adequacy_module = importlib.import_module("rtdsl.current_benchmark_adequacy")
        adequacy = {
            row["app"]: row for row in adequacy_module.current_benchmark_adequacy()
        }["rtnn"]

        self.assertEqual(
            "rtdl.v3_0.current_benchmark_route_decisions.goal4507.v1",
            route["version"],
        )
        self.assertEqual(
            "rtdl.v3_0.current_benchmark_adequacy.goal4507.v1",
            adequacy["version"],
        )
        self.assertIn("Goal4504", route["evidence_refs"])
        self.assertIn("Goal4504", adequacy["evidence_refs"])
        self.assertIn("size-aware", route["current_reader_decision"])
        self.assertIn("size-aware", adequacy["current_recommended_path"])

    def test_invalid_query_size_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            rt.plan_v2_5_fixed_radius_aggregate_execution_path(
                requires_partner_continuation=False,
                query_count=0,
            )
        with self.assertRaises(ValueError):
            rt.plan_v2_5_fixed_radius_aggregate_execution_path(
                requires_partner_continuation=False,
                query_batch_size=-1,
            )


if __name__ == "__main__":
    unittest.main()
