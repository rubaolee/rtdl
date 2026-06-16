from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal4459_v3_0_m63_rtnn_clustered_app_bridge_2026-06-16.md"
EVIDENCE = (
    ROOT
    / "docs/reports/goal4459_v3_0_m63_rtnn_app_bridge_clustered_1048576q65536_r1000_2026-06-16.json"
)
RTNN_README = ROOT / "examples/current/research_benchmarks/rtnn/README.md"
EVIDENCE_INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
PARTNER_MATRIX = ROOT / "docs/learn/benchmark_partner_reference_matrix.md"
RT_CORE_MATRIX = ROOT / "docs/learn/rt_core_evidence_matrix.md"


class Goal4459V30M63RtnnClusteredAppBridgeTest(unittest.TestCase):
    def test_clustered_app_bridge_artifact_is_large_and_signature_clean(self) -> None:
        payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        compact = payload["compact_summary"]

        self.assertEqual(payload["benchmark_app"], "rtnn_neighbor_search")
        self.assertEqual(payload["mode"], "prepared_ranked_summary_graph_partner_bridge")
        self.assertEqual(compact["distribution"], "clustered")
        self.assertEqual(compact["point_count"], 1_048_576)
        self.assertEqual(compact["query_count"], 65_536)
        self.assertEqual(compact["repeats"], 1000)
        self.assertEqual(compact["warmups"], 2)
        self.assertEqual(compact["partners"], ["cupy", "numba"])
        self.assertTrue(compact["signature_match"])
        self.assertTrue(compact["hot_no_hidden_column_copy_ready"])
        self.assertTrue(compact["device_result_materialization_after_hot_window"])
        self.assertFalse(compact["public_claim_authorized"])

        cupy = compact["partner_rows"]["cupy"]
        numba = compact["partner_rows"]["numba"]
        cupy_hot = float(cupy["hot_device_run_seconds_median"])
        numba_hot = float(numba["hot_device_run_seconds_median"])

        self.assertGreater(cupy_hot, 0.12)
        self.assertLess(cupy_hot, 0.14)
        self.assertGreater(numba_hot, 0.12)
        self.assertLess(numba_hot, 0.14)
        self.assertGreater(cupy_hot * compact["repeats"], 120.0)
        self.assertGreater(numba_hot * compact["repeats"], 120.0)
        self.assertLess(numba_hot / cupy_hot, 1.05)

        for row in (cupy, numba):
            self.assertTrue(row["cuda_graph_replay_used"])
            self.assertTrue(row["same_stream_partner_device_reduction_used"])
            self.assertTrue(row["hot_no_hidden_column_copy_ready"])
            self.assertTrue(row["device_result_materialization_after_hot_window"])

    def test_clustered_app_bridge_updates_docs_and_route_registry(self) -> None:
        route = rt.explain_current_benchmark_route("rtnn")
        adequacy = {row["app"]: row for row in rt.current_benchmark_adequacy()}["rtnn"]
        report = REPORT.read_text(encoding="utf-8")
        readme = RTNN_README.read_text(encoding="utf-8")
        evidence_index = EVIDENCE_INDEX.read_text(encoding="utf-8")
        partner_matrix = PARTNER_MATRIX.read_text(encoding="utf-8")
        rt_core_matrix = RT_CORE_MATRIX.read_text(encoding="utf-8")

        self.assertEqual(
            "rtdl.v3_0.current_benchmark_route_decisions.goal4473.v1",
            route["version"],
        )
        self.assertIn("Goal4459", route["evidence_refs"])
        self.assertIn("clustered", route["current_reader_decision"])
        self.assertIn("130.079ms", route["current_reader_decision"])
        self.assertIn("131.442ms", route["current_reader_decision"])
        self.assertIn("distribution", route["user_choice_guidance"])
        self.assertIn(
            "treating the clustered resident app bridge as a full RTNN paper row",
            route["rejected_or_unpromoted_candidates"],
        )
        self.assertFalse(route["paper_reproduction_claim_authorized"])
        self.assertFalse(route["automatic_partner_selection_authorized"])

        self.assertEqual(
            "rtdl.v3_0.current_benchmark_adequacy.goal4473.v1",
            adequacy["version"],
        )
        self.assertEqual("strong", adequacy["adequacy"])
        self.assertIn("Goal4459", adequacy["evidence_refs"])
        self.assertIn("clustered 1M resident", adequacy["current_performance_reading"])
        self.assertFalse(adequacy["public_speedup_claim_authorized"])

        for text in (report, readme, evidence_index, partner_matrix, rt_core_matrix):
            self.assertIn("Goal4459", text)
            self.assertIn("clustered", text)
        self.assertIn("not a full RTNN paper row", readme)
        self.assertIn("It is not full RTNN paper reproduction", report)


if __name__ == "__main__":
    unittest.main()


