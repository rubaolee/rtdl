from __future__ import annotations

import pathlib
import unittest

from examples.v2_0.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    RT_DBSCAN_GROUPED_STREAM_TIMING_BREAKDOWN_SCHEMA,
    _build_grouped_stream_timing_breakdown,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
RUNNER = ROOT / "scripts" / "goal2467_grouped_stream_baseline_pod_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal2468_rt_dbscan_overhead_breakdown_instrumentation_2026-05-20.md"
POD_REPORT = ROOT / "docs" / "reports" / "goal2468_grouped_stream_overhead_pod_2026-05-20.md"
POD_SUMMARY = ROOT / "docs" / "reports" / "goal2468_grouped_stream_overhead_pod" / "summary.json"


class Goal2468RtDbscanOverheadBreakdownInstrumentationTest(unittest.TestCase):
    def test_timing_breakdown_computes_native_and_non_native_gap(self) -> None:
        metadata = {
            "core_flag_cache_reused": False,
            "count_metadata": {"native_metadata": {"native_elapsed_sec": 0.004}},
            "native_grouped_stream_metadata": {"native_elapsed_sec": 0.070},
        }

        breakdown = _build_grouped_stream_timing_breakdown(
            {
                "adapter_run_sec": 0.120,
                "rows_materialization_sec": 0.030,
                "densify_cluster_labels_sec": 0.010,
            },
            metadata,
            elapsed_sec=0.175,
        )

        self.assertEqual(breakdown["schema"], RT_DBSCAN_GROUPED_STREAM_TIMING_BREAKDOWN_SCHEMA)
        self.assertFalse(breakdown["performance_claim_authorized"])
        derived = breakdown["derived_sec"]
        self.assertAlmostEqual(derived["known_native_current_run_sec"], 0.074)
        self.assertAlmostEqual(derived["adapter_non_native_estimated_sec"], 0.046)
        self.assertAlmostEqual(derived["unattributed_elapsed_sec"], 0.015)

    def test_cache_hit_excludes_old_count_native_time_from_current_run(self) -> None:
        metadata = {
            "core_flag_cache_reused": True,
            "count_metadata": {"native_metadata": {"native_elapsed_sec": 0.004}},
            "native_grouped_stream_metadata": {"native_elapsed_sec": 0.070},
        }

        breakdown = _build_grouped_stream_timing_breakdown(
            {"adapter_run_sec": 0.120},
            metadata,
            elapsed_sec=0.121,
        )

        derived = breakdown["derived_sec"]
        self.assertEqual(derived["count_native_current_run_sec"], 0.0)
        self.assertAlmostEqual(derived["known_native_current_run_sec"], 0.070)
        self.assertAlmostEqual(derived["adapter_non_native_estimated_sec"], 0.050)

    def test_app_and_runner_record_breakdown_without_claiming_speedup(self) -> None:
        app = APP.read_text(encoding="utf-8")
        runner = RUNNER.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("benchmark_timing_breakdown", app)
        self.assertIn("adapter_run_sec", app)
        self.assertIn("rows_materialization_sec", app)
        self.assertIn("densify_cluster_labels_sec", app)
        self.assertIn("adapter_non_native_estimated_sec", app)
        self.assertIn("_build_grouped_stream_timing_breakdown", runner)
        self.assertIn("signature_sec", runner)
        self.assertIn("timing_breakdown", runner)
        self.assertIn("tail_timing_breakdown_median_sec", runner)
        self.assertIn("adapter_non_native_estimated_sec", runner)
        self.assertIn("no new pod measurement", report)
        self.assertIn("does not authorize a performance claim", report)

    def test_pod_overhead_evidence_attributes_gap_to_row_handling(self) -> None:
        import json

        report = POD_REPORT.read_text(encoding="utf-8")
        summary = json.loads(POD_SUMMARY.read_text(encoding="utf-8"))

        self.assertIn("NVIDIA RTX PRO 4500 Blackwell", report)
        self.assertIn("row materialization plus", report)
        self.assertIn("No broad RT-core speedup", report)
        self.assertEqual(summary["gpu"], "NVIDIA RTX PRO 4500 Blackwell, 580.126.20")
        self.assertTrue(summary["tiny_smoke_matches_reference"])
        self.assertEqual([row["point_count"] for row in summary["summaries"]], [32768, 65536])

        for row in summary["summaries"]:
            self.assertTrue(row["signatures_match"])
            breakdown = row["tail_timing_breakdown_median_sec"]
            self.assertEqual(breakdown["schema"], RT_DBSCAN_GROUPED_STREAM_TIMING_BREAKDOWN_SCHEMA)
            host = breakdown["host_observed"]
            derived = breakdown["derived"]
            self.assertGreater(row["tail_median_sec"], row["grouped_native_tail_median_sec"])
            self.assertGreater(host["rows_materialization_sec"], 0.0)
            self.assertGreater(host["densify_cluster_labels_sec"], 0.0)
            self.assertGreater(host["signature_sec"], 0.0)
            self.assertLess(derived["adapter_non_native_estimated_sec"], 0.001)
            self.assertAlmostEqual(
                derived["grouped_native_sec"],
                row["grouped_native_tail_median_sec"],
                places=9,
            )


if __name__ == "__main__":
    unittest.main()
