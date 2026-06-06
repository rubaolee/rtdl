from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3660_rayjoin_pip_batch_executor_throughput_2026-06-06.md"
SUMMARY = ROOT / "docs" / "reports" / "goal3660_rayjoin_pip_batch_executor_throughput_a5000" / "summary.json"
RUNNER = ROOT / "scripts" / "goal3244_rayjoin_same_slice_repeated_count_runner.py"
APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "spatial_rayjoin"
    / "rtdl_rayjoin_v2_spatial_join_app.py"
)


class Goal3660RayJoinPipBatchExecutorThroughputTest(unittest.TestCase):
    def test_report_is_bounded_and_distinguishes_batched_throughput_from_one_shot(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "batched repeated-request throughput",
            "not one-shot latency",
            "not a drop-in replacement",
            "does not prove full RayJoin paper reproduction",
            "0.034225ms/request",
            "0.178x",
            "Goal3658 sequential RTDL route",
            "`12.79x` faster",
            "does not authorize",
            "app-specific native-engine logic",
        ):
            self.assertIn(phrase, text)

    def test_clean_a5000_artifact_supports_batched_throughput_finding(self) -> None:
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
        rtdl = payload["rtdl"]["pip"]
        rayjoin = payload["rayjoin"]["pip"]
        comparison = payload["comparisons"][0]

        self.assertEqual(payload["source_dirty"], [])
        self.assertEqual(payload["rtdl_commit"][:8], "def665eb")
        self.assertEqual(rtdl["counts"]["last"], 1417)
        self.assertEqual(rtdl["pip_timing_contract"], "batched_repeated_request_throughput_not_one_shot_latency")
        self.assertEqual(rtdl["pip_batch_request_count"], 100)
        self.assertEqual(rtdl["pip_batch_stream_count"], "auto")
        self.assertEqual(rtdl["internal_query_repeat"], 30000)
        self.assertEqual(rtdl["internal_warmup"], 100)
        self.assertLess(rtdl["prepared_query_ms"]["median"], 0.04)
        self.assertGreater(rtdl["prepared_query_total_ms"]["median"], 1000.0)
        self.assertLess(rtdl["prepared_query_total_ms"]["median"], 1100.0)
        self.assertLess(comparison["rtdl_over_rayjoin_query_ratio"], 0.2)
        self.assertGreater(rayjoin["process_wall_ms"]["median"], 6000.0)
        self.assertFalse(rayjoin["positive_assignment_count_available"])
        self.assertTrue(all(value is False for value in payload["claim_boundary"].values()))

    def test_runner_and_app_expose_explicit_batch_contract(self) -> None:
        runner = RUNNER.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")

        for phrase in (
            "--rtdl-pip-batch-request-count",
            "--rtdl-pip-batch-stream-count",
            "batched_repeated_request_throughput_not_one_shot_latency",
            "must not be read as a",
            "drop-in replacement",
        ):
            self.assertIn(phrase, runner)
        for phrase in (
            "def _phase_batched_count_executor_repeat_time",
            "prepare_device_filtered_prepared_points_batch_executor",
            "query_repeat must be divisible by batch_request_count",
            "batched_repeated_request_throughput_not_one_shot_latency",
        ):
            self.assertIn(phrase, app)


if __name__ == "__main__":
    unittest.main()
