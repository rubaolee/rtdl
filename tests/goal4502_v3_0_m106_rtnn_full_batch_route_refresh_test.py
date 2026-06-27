from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4502_v3_0_m106_rtnn_full_batch_route_refresh_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4502_v3_0_m106_rtnn_full_batch_route_refresh_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
README = ROOT / "examples/benchmark_apps/rtnn/README.md"
SCRIPT = ROOT / "scripts/goal4502_m106_rtnn_full_batch_route_refresh.py"


class Goal4502V30M106RtnnFullBatchRouteRefreshTest(unittest.TestCase):
    def test_script_rebuilds_packet_from_raw_evidence(self) -> None:
        module = importlib.import_module("scripts.goal4502_m106_rtnn_full_batch_route_refresh")
        packet = module.build_packet(ROOT)
        best = packet["rtdl"]["optix_full_batch_direct_aggregate"]

        self.assertEqual("rtdl.v3_0.rtnn_full_batch_route_refresh.goal4502.v1", packet["version"])
        self.assertEqual("Goal4502 / V3 M106", packet["goal"])
        self.assertEqual(1_000_000, packet["input_contract"]["point_count"])
        self.assertEqual(1_000_000, best["query_batch_size"])
        self.assertEqual("ranked-summary-aggregate-prepared-query-batch-float32", best["result_mode"])
        self.assertLess(best["median_query_sec"], 0.2)
        self.assertGreater(packet["comparisons"]["rtdl_full_batch_over_direct_graph_query"], 1.5)
        self.assertGreater(packet["comparisons"]["rtdl_full_batch_query_over_author_total_search"], 2.0)
        self.assertGreater(packet["comparisons"]["author_compute_over_rtdl_full_batch_query"], 10.0)
        self.assertFalse(packet["claim_boundary"]["graph_mode_required_for_aggregate_only"])
        self.assertTrue(packet["claim_boundary"]["same_stream_partner_required_only_for_continuation"])

    def test_report_docs_and_guidance_are_refreshed(self) -> None:
        packet = json.loads(PACKET.read_text(encoding="utf-8"))
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")
        route = rt.explain_current_benchmark_route("rtnn")
        adequacy_module = importlib.import_module("rtdsl.current_benchmark_adequacy")
        adequacy = {
            row["app"]: row for row in adequacy_module.current_benchmark_adequacy()
        }["rtnn"]

        self.assertEqual("rtdl.v3_0.rtnn_full_batch_route_refresh.goal4502.v1", packet["version"])
        self.assertIn("Full-batch prepared direct aggregate", report)
        self.assertIn("Graph Cap Audit", report)
        self.assertIn("Goal4502 RTNN full-batch route refresh", index)
        self.assertIn("Goal4502 then reranks", readme)
        self.assertIn("SWEEP_GLOB", script)
        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4507.v1", route["version"])
        self.assertEqual("rtdl.v3_0.current_benchmark_adequacy.goal4507.v1", adequacy["version"])
        self.assertIn("Goal4502", route["evidence_refs"])
        self.assertIn("Goal4502", adequacy["evidence_refs"])
        self.assertIn("full-batch", route["primary_route"])
        self.assertIn("full-batch", adequacy["current_recommended_path"])
        self.assertIn("graph/device-partial", route["primary_route"])
        self.assertIn("graph partner bridge", adequacy["next_generic_runtime_action"])


if __name__ == "__main__":
    unittest.main()
