from __future__ import annotations

from pathlib import Path
import json
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3842_rayjoin_pip_batch_executor_current_refresh_2026-06-08.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3842_rayjoin_pip_batch_executor_current_a5000" / "summary.json"


class Goal3842RayJoinPipBatchExecutorCurrentRefreshTest(unittest.TestCase):
    def test_artifact_records_current_main_exact_batch_evidence(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["rtdl_commit"], "09a31f30717ce53624df6bc4b73b1b80a81d4eb7")
        self.assertEqual(payload["exact_count"], 1417)
        self.assertEqual(payload["dataset"].split("/")[-1], "br_county_start256_count512.cdb")
        rows = {int(row["request_count"]): row for row in payload["batch_rows"]}
        self.assertEqual(rows[1]["count_first"], 1417)
        self.assertEqual(rows[100]["count_last"], 1417)
        self.assertLess(rows[100]["per_request_ms_median"], 0.025)
        self.assertLess(
            rows[100]["per_request_ms_median"],
            rows[1]["per_request_ms_median"] / 8.0,
        )
        self.assertFalse(any(payload["claim_boundary"].values()))

    def test_current_adequacy_records_pip_batch_lane_without_overclaim(self) -> None:
        self.assertEqual(
            rt.CURRENT_BENCHMARK_ADEQUACY_VERSION,
            "rtdl.v2_10.benchmark_adequacy_after_goal3936.v1",
        )
        spatial = {row["app"]: row for row in rt.current_benchmark_adequacy()}["spatial_rayjoin"]
        self.assertIn("Goal3842", spatial["evidence_refs"])
        self.assertIn("100-request median 0.024183ms/request", spatial["current_performance_reading"])
        self.assertIn("not one-shot latency", spatial["current_performance_reading"])
        self.assertIn("batch executor", spatial["current_recommended_path"])
        self.assertIn("zero-count replay failure", spatial["next_generic_runtime_action"])
        self.assertFalse(spatial["paper_reproduction_claim_authorized"])
        self.assertFalse(spatial["public_speedup_claim_authorized"])

    def test_report_documents_graph_replay_negative_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3842 RayJoin PIP Batch Executor", text)
        self.assertIn("RTDL_OPTIX_POINT_PRIMITIVE_DEVICE_PREDICATE_EPS=1e-9", text)
        self.assertIn("9.04x", text)
        self.assertIn("Graph Replay Check", text)
        self.assertIn("zero-count", text)
        self.assertIn("does not authorize", text)


if __name__ == "__main__":
    unittest.main()
