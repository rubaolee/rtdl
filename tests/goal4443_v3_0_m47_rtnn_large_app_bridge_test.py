from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal4443_v3_0_m47_rtnn_large_app_bridge_2026-06-16.md"
EVIDENCE = ROOT / "docs/reports/goal4443_v3_0_m47_rtnn_app_bridge_uniform_1048576q65536_r1000_2026-06-16.json"
GOAL4381_DIR = ROOT / "docs/reports/goal4381_rtnn_aggregate_large_2026-06-14"
EMBREE_1M = GOAL4381_DIR / "rtnn_uniform_1m_embree_aggregate_exact_repeat3.json"
OPTIX_1M = GOAL4381_DIR / "rtnn_uniform_1m_optix_aggregate_exact_repeat100.json"
EVIDENCE_INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
PARTNER_MATRIX = ROOT / "docs/learn/benchmark_partner_reference_matrix.md"
RT_CORE_MATRIX = ROOT / "docs/learn/rt_core_evidence_matrix.md"
RTNN_README = ROOT / "examples/current/research_benchmarks/rtnn/README.md"


class Goal4443V30M47RtnnLargeAppBridgeTest(unittest.TestCase):
    def test_large_app_bridge_artifact_has_second_level_hot_evidence(self) -> None:
        payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        compact = payload["compact_summary"]

        self.assertEqual(payload["mode"], "prepared_ranked_summary_graph_partner_bridge")
        self.assertEqual(compact["point_count"], 1_048_576)
        self.assertEqual(compact["query_count"], 65_536)
        self.assertEqual(compact["repeats"], 1000)
        self.assertEqual(compact["warmups"], 2)
        self.assertEqual(compact["partners"], ["cupy", "numba"])
        self.assertTrue(compact["signature_match"])
        self.assertTrue(compact["hot_no_hidden_column_copy_ready"])
        self.assertTrue(compact["device_result_materialization_after_hot_window"])
        self.assertFalse(compact["public_claim_authorized"])

        for partner in ("cupy", "numba"):
            row = compact["partner_rows"][partner]
            hot = float(row["hot_device_run_seconds_median"])
            self.assertGreater(hot, 0.004)
            self.assertLess(hot, 0.006)
            self.assertGreater(hot * compact["repeats"], 4.0)
            self.assertTrue(row["cuda_graph_replay_used"])
            self.assertTrue(row["same_stream_partner_device_reduction_used"])
            self.assertTrue(row["hot_no_hidden_column_copy_ready"])

    def test_large_app_bridge_speedups_are_read_at_matching_query_granularity(self) -> None:
        payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        embree = json.loads(EMBREE_1M.read_text(encoding="utf-8"))
        optix = json.loads(OPTIX_1M.read_text(encoding="utf-8"))
        compact = payload["compact_summary"]
        batch_count = compact["point_count"] // compact["query_count"]

        self.assertEqual(batch_count, 16)
        self.assertEqual(embree["result_mode"], "ranked-summary-aggregate")
        self.assertEqual(optix["result_mode"], "ranked-summary-aggregate")
        self.assertEqual(embree["query_count"], compact["point_count"])
        self.assertEqual(optix["query_count"], compact["point_count"])

        for partner in ("cupy", "numba"):
            hot = float(compact["partner_rows"][partner]["hot_device_run_seconds_median"])
            estimated_full_query_total = hot * batch_count
            self.assertGreater(float(embree["elapsed_median_sec"]) / estimated_full_query_total, 18.0)
            self.assertGreater(float(optix["elapsed_median_sec"]) / estimated_full_query_total, 1.8)

    def test_docs_and_route_registry_carry_m47_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        evidence_index = EVIDENCE_INDEX.read_text(encoding="utf-8")
        partner_matrix = PARTNER_MATRIX.read_text(encoding="utf-8")
        rt_core_matrix = RT_CORE_MATRIX.read_text(encoding="utf-8")
        readme = RTNN_README.read_text(encoding="utf-8")
        route = rt.explain_current_benchmark_route("rtnn")
        validation = rt.validate_current_benchmark_route_decisions()

        self.assertEqual("accept", validation["status"])
        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4486.v1", route["version"])
        self.assertEqual("mixed_explicit", route["decision_kind"])
        self.assertEqual("mixed_explicit_user_choice", route["partner_policy"])
        self.assertIn("Goal4443", route["evidence_refs"])
        self.assertIn("exact float64 RTDL/OptiX native ranked-summary aggregate", route["current_reader_decision"])
        self.assertIn("prepared_ranked_summary_graph_partner_bridge", route["current_reader_decision"])
        self.assertIn("automatic exact-vs-float32 route selection", route["rejected_or_unpromoted_candidates"])
        self.assertFalse(route["public_speedup_claim_authorized"])

        for text in (report, evidence_index, partner_matrix, rt_core_matrix, readme):
            self.assertIn("Goal4443", text)
        self.assertIn("about `5ms` hot median per batch", readme)
        self.assertIn("not full RTNN paper reproduction", report)


if __name__ == "__main__":
    unittest.main()


