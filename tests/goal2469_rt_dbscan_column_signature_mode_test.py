from __future__ import annotations

import json
import pathlib
import unittest

from examples.v2_0.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    _cluster_signature_from_host_columns,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
RUNNER = ROOT / "scripts" / "goal2467_grouped_stream_baseline_pod_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal2469_rt_dbscan_column_signature_mode_2026-05-20.md"
POD_REPORT = ROOT / "docs" / "reports" / "goal2469_grouped_stream_column_signature_pod_2026-05-20.md"
GEMINI_REVIEW = ROOT / "docs" / "reviews" / "goal2469_gemini_review_column_signature_pod_2026-05-20.md"
CONSENSUS = ROOT / "docs" / "reviews" / "goal2469_codex_gemini_consensus_column_signature_pod_2026-05-20.md"
ROW_POD_SUMMARY = ROOT / "docs" / "reports" / "goal2469_grouped_stream_row_signature_pod" / "summary.json"
COLUMN_POD_SUMMARY = ROOT / "docs" / "reports" / "goal2469_grouped_stream_column_signature_pod" / "summary.json"


class Goal2469RtDbscanColumnSignatureModeTest(unittest.TestCase):
    def test_host_column_signature_matches_dense_row_signature_shape(self) -> None:
        signature = _cluster_signature_from_host_columns(
            point_ids=[2, 0, 3, 1, 4],
            component_labels=[40, 20, -1, 20, 40],
            core_flags=[0, 1, 0, 1, 1],
        )

        self.assertEqual(
            signature,
            {
                "cluster_sizes": {1: 2, 2: 2},
                "core_count": 3,
                "noise_count": 1,
            },
        )

    def test_app_exposes_column_signature_mode_without_python_rows(self) -> None:
        app = APP.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("optix_rt_core_grouped_stream_cupy_column_signature_3d", app)
        self.assertIn("partner_column_arrays_no_python_row_dicts", app)
        self.assertIn("materializes_python_rows", app)
        self.assertIn("column_signature_sec", app)
        self.assertIn("column-signature mode does not materialize Python rows", app)
        self.assertIn("no-row benchmark mode", report)
        self.assertIn("does not add a native ABI", report)

    def test_runner_can_compare_row_and_column_signature_modes(self) -> None:
        runner = RUNNER.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("--signature-mode", runner)
        self.assertIn("choices=(\"row\", \"column\")", runner)
        self.assertIn("_cluster_signature_from_partner_columns", runner)
        self.assertIn("column_signature_sec", runner)
        self.assertIn("signature_mode", runner)
        self.assertIn("same prepared-handle repeat protocol", report)

    def test_pod_evidence_records_column_signature_host_overhead_win(self) -> None:
        row = json.loads(ROW_POD_SUMMARY.read_text(encoding="utf-8"))
        column = json.loads(COLUMN_POD_SUMMARY.read_text(encoding="utf-8"))
        report = POD_REPORT.read_text(encoding="utf-8")

        self.assertIn("NVIDIA RTX 2000 Ada Generation", row["gpu"])
        self.assertEqual(row["signature_mode"], "row")
        self.assertEqual(column["signature_mode"], "column")
        self.assertIn("OptiX 8.0", report)
        self.assertIn("Unsupported ABI version", report)
        self.assertIn("does not claim a faster native RT primitive", report)

        by_points = {
            row_item["point_count"]: (row_item, column_item)
            for row_item, column_item in zip(row["summaries"], column["summaries"])
        }
        self.assertEqual(set(by_points), {32768, 65536})
        for point_count, (row_item, column_item) in by_points.items():
            with self.subTest(point_count=point_count):
                self.assertLess(column_item["tail_median_sec"], row_item["tail_median_sec"])
                self.assertTrue(row_item["signatures_match"])
                self.assertTrue(column_item["signatures_match"])
                row_native = row_item["grouped_native_tail_median_sec"]
                column_native = column_item["grouped_native_tail_median_sec"]
                row_gap = row_item["tail_median_sec"] - row_native
                column_gap = column_item["tail_median_sec"] - column_native
                self.assertLess(column_gap, row_gap)
                self.assertLess(abs(row_native - column_native), row_gap - column_gap)
                row_host = row_item["tail_timing_breakdown_median_sec"]["host_observed"]
                column_host = column_item["tail_timing_breakdown_median_sec"]["host_observed"]
                self.assertIn("rows_materialization_sec", row_host)
                self.assertIn("densify_cluster_labels_sec", row_host)
                self.assertIn("column_signature_sec", column_host)
                self.assertNotIn("rows_materialization_sec", column_host)
                self.assertNotIn("densify_cluster_labels_sec", column_host)

    def test_external_review_accepts_narrow_column_signature_claim(self) -> None:
        gemini = GEMINI_REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("ACCEPT", gemini)
        self.assertIn("host-side overhead reduction", consensus)
        self.assertIn("not a claim that the native RT primitive became faster", consensus)
        self.assertIn("does not add a DBSCAN-specific native ABI", consensus)


if __name__ == "__main__":
    unittest.main()
