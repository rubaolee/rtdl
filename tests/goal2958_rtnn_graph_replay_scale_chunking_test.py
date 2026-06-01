from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts import goal2800_rtnn_v25_live_ranked_summary_harness as harness


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2958_rtnn_graph_replay_scale_chunking_2026-06-01.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2958_rtnn_graph_replay_scale_pod" / "goal2958_rtnn_graph_131k.json"


class Goal2958RtnnGraphReplayScaleChunkingTest(unittest.TestCase):
    def test_harness_defaults_to_graph_safe_batch_limit(self) -> None:
        self.assertEqual(65536, harness.GOAL2800_GRAPH_REPLAY_QUERY_BATCH_LIMIT)
        self.assertEqual("ranked-summary-aggregate-prepared-query-batch-graph-float32", harness.GOAL2800_RESULT_MODE)

    def test_131k_pod_artifact_uses_two_batches_and_passes(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual("pass", payload["status"])
        self.assertEqual([], payload["source_dirty"])
        self.assertEqual(131072, payload["point_count"])
        self.assertEqual(65536, payload["query_batch_size"])
        for row in payload["rows"]:
            with self.subTest(distribution=row["distribution"]):
                self.assertEqual(2, row["rtdl_phase_summary"]["batch_count"])
                self.assertEqual("ranked-summary-aggregate-prepared-query-batch-graph-float32", row["contract"]["mode"])
                self.assertTrue(row["ranked_aggregate_matches_cupy_grid"])
                self.assertGreater(float(row["cupy_grid_over_rtdl_elapsed_ratio"]), 1.0)
                self.assertEqual(0.0, float(row["rtdl_phase_summary"]["upload_sec"]))
                self.assertFalse(row["claim_boundary"]["rtdl_beats_cupy_grid_claim_authorized"])

    def test_report_documents_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2958",
            "GOAL2800_GRAPH_REPLAY_QUERY_BATCH_LIMIT = 65536",
            "`1.711x`",
            "`2.435x`",
            "`12.296x`",
            "does not add RTNN-specific native engine code",
            "does not authorize",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
