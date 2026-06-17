from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4507_v3_0_m111_rtnn_chunked_distribution_matrix_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4507_v3_0_m111_rtnn_chunked_distribution_matrix_2026-06-17.md"
README = ROOT / "examples/current/research_benchmarks/rtnn/README.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4507V30M111RtnnChunkedDistributionMatrixTest(unittest.TestCase):
    def test_script_rebuilds_three_distribution_chunked_matrix(self) -> None:
        module = importlib.import_module("scripts.goal4507_m111_rtnn_chunked_distribution_matrix")
        packet = module.build_packet(ROOT)
        rows = {row["distribution"]: row for row in packet["rows"]}

        self.assertEqual("rtdl.v3_0.rtnn_chunked_distribution_matrix.goal4507.v1", packet["version"])
        self.assertEqual(("uniform", "shell", "clustered"), packet["matrix_summary"]["distributions"])
        self.assertTrue(packet["matrix_summary"]["all_signature_match"])
        self.assertTrue(packet["matrix_summary"]["all_hot_no_hidden_column_copy_ready"])
        self.assertTrue(packet["matrix_summary"]["all_prepared_scene_reused_across_chunks"])
        self.assertEqual("uniform", packet["matrix_summary"]["fastest_distribution_by_cupy_hot_sum"])
        self.assertEqual("clustered", packet["matrix_summary"]["slowest_distribution_by_cupy_hot_sum"])
        self.assertEqual(16, rows["uniform"]["chunk_count"])
        self.assertEqual(16, rows["shell"]["chunk_count"])
        self.assertEqual(16, rows["clustered"]["chunk_count"])
        self.assertLess(rows["uniform"]["cupy_hot_device_run_seconds_median_sum"], rows["shell"]["cupy_hot_device_run_seconds_median_sum"])
        self.assertLess(rows["shell"]["cupy_hot_device_run_seconds_median_sum"], rows["clustered"]["cupy_hot_device_run_seconds_median_sum"])
        self.assertFalse(packet["claim_boundary"]["aggregate_only_full_batch_direct_comparison_authorized"])

    def test_report_docs_and_current_registry_include_goal4507(self) -> None:
        packet = json.loads(PACKET.read_text(encoding="utf-8"))
        report = REPORT.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        route = rt.explain_current_benchmark_route("rtnn")
        adequacy = {row["app"]: row for row in rt.current_benchmark_adequacy()}["rtnn"]

        self.assertEqual("rtdl.v3_0.rtnn_chunked_distribution_matrix.goal4507.v1", packet["version"])
        self.assertIn("uniform", report)
        self.assertIn("shell", report)
        self.assertIn("clustered", report)
        self.assertIn("0.609413s", report)
        self.assertIn("2.041410s", report)
        self.assertIn("Goal4507", readme)
        self.assertIn("Goal4507 RTNN chunked distribution matrix", index)
        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4507.v1", route["version"])
        self.assertEqual("rtdl.v3_0.current_benchmark_adequacy.goal4507.v1", adequacy["version"])
        self.assertIn("Goal4507", route["evidence_refs"])
        self.assertIn("Goal4507", adequacy["evidence_refs"])
        self.assertIn("0.609s", route["current_reader_decision"])
        self.assertIn("2.04s", route["current_reader_decision"])


if __name__ == "__main__":
    unittest.main()
