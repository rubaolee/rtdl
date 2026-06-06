from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3663_rayjoin_pip_batch_executor_cross_slice_2026-06-06.md"
SUMMARY_512 = ROOT / "docs" / "reports" / "goal3660_rayjoin_pip_batch_executor_throughput_a5000" / "summary.json"
SUMMARY_4096 = ROOT / "docs" / "reports" / "goal3663_rayjoin_pip_batch_executor_cross_slice_a5000" / "summary_4096.json"


class Goal3663RayJoinPipBatchExecutorCrossSliceTest(unittest.TestCase):
    def test_report_records_cross_slice_confirmation_without_overclaiming(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "not one-shot latency",
            "not full RayJoin paper reproduction",
            "512 slice",
            "4096 slice",
            "0.034225",
            "0.051139",
            "second-GPU confirmation remains future work",
            "does not authorize",
            "app-specific native-engine logic",
        ):
            self.assertIn(phrase, text)

    def test_512_and_4096_artifacts_support_same_batched_contract(self) -> None:
        small = json.loads(SUMMARY_512.read_text(encoding="utf-8"))
        large = json.loads(SUMMARY_4096.read_text(encoding="utf-8"))

        small_rtdl = small["rtdl"]["pip"]
        large_rtdl = large["rtdl"]["pip"]

        self.assertEqual(small["source_dirty"], [])
        self.assertEqual(large["source_dirty"], [])
        self.assertEqual(small_rtdl["counts"]["last"], 1417)
        self.assertEqual(large_rtdl["counts"]["last"], 11331)
        self.assertEqual(
            small_rtdl["pip_timing_contract"],
            "batched_repeated_request_throughput_not_one_shot_latency",
        )
        self.assertEqual(
            large_rtdl["pip_timing_contract"],
            "batched_repeated_request_throughput_not_one_shot_latency",
        )
        self.assertEqual(large_rtdl["pip_batch_request_count"], 100)
        self.assertEqual(large_rtdl["pip_batch_stream_count"], "auto")
        self.assertEqual(large_rtdl["internal_query_repeat"], 30000)
        self.assertLess(small["comparisons"][0]["rtdl_over_rayjoin_query_ratio"], 0.18 + 0.01)
        self.assertLess(large["comparisons"][0]["rtdl_over_rayjoin_query_ratio"], 0.12)
        self.assertGreater(large["rayjoin"]["pip"]["process_wall_ms"]["median"], 15000.0)
        self.assertGreater(large_rtdl["prepared_query_total_ms"]["median"], 1500.0)
        self.assertTrue(all(value is False for value in large["claim_boundary"].values()))


if __name__ == "__main__":
    unittest.main()
