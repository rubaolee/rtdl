from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts import goal2800_rtnn_v25_live_ranked_summary_harness as harness


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "scripts" / "goal2800_rtnn_v25_live_ranked_summary_harness.py"
REPORT = ROOT / "docs" / "reports" / "goal2954_rtnn_graph_replay_route_tuning_2026-06-01.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2954_rtnn_graph_replay_sweep_pod"


class Goal2954RtnnGraphReplayRouteTuningTest(unittest.TestCase):
    def test_canonical_harness_uses_graph_replay_route(self) -> None:
        text = HARNESS.read_text(encoding="utf-8")

        self.assertIn("v8.scale65536_repeat9_graph_replay", text)
        self.assertEqual("ranked-summary-aggregate-prepared-query-batch-graph-float32", harness.GOAL2800_RESULT_MODE)
        self.assertEqual(65536, harness.GOAL2800_GRAPH_REPLAY_QUERY_BATCH_LIMIT)
        self.assertIn("result_mode=GOAL2800_RESULT_MODE", text)
        self.assertNotIn(
            'result_mode="ranked-summary-aggregate-prepared-query-float32"',
            text,
        )
        self.assertIn("min(int(point_count), GOAL2800_GRAPH_REPLAY_QUERY_BATCH_LIMIT)", text)

    def test_uniform_mode_sweep_selects_graph_replay(self) -> None:
        payload = json.loads((ARTIFACT_DIR / "goal2954_rtnn_uniform_mode_sweep.json").read_text(encoding="utf-8"))

        self.assertEqual([], payload["source_dirty"])
        rows = {row["mode"]: row for row in payload["rows"]}
        graph = rows["ranked-summary-aggregate-prepared-query-batch-graph-float32"]
        prepared = rows["ranked-summary-aggregate-prepared-query-float32"]
        batch = rows["ranked-summary-aggregate-prepared-query-batch-float32"]
        same_stream = rows["ranked-summary-aggregate-prepared-query-batch-graph-same-stream-cupy-float32"]

        self.assertGreater(float(graph["cupy_over_rtdl_ratio"]), 1.0)
        self.assertLess(float(graph["median_sec"]), float(prepared["median_sec"]))
        self.assertLess(float(graph["median_sec"]), float(batch["median_sec"]))
        self.assertLess(float(graph["median_sec"]), float(same_stream["median_sec"]))

    def test_graph_replay_preserves_contract_across_distributions(self) -> None:
        payload = json.loads(
            (ARTIFACT_DIR / "goal2954_rtnn_graph_all_distributions.json").read_text(encoding="utf-8")
        )

        self.assertEqual([], payload["source_dirty"])
        self.assertEqual("ranked-summary-aggregate-prepared-query-batch-graph-float32", payload["mode"])
        ratios = {row["distribution"]: float(row["cupy_over_rtdl_ratio"]) for row in payload["rows"]}
        self.assertGreater(ratios["uniform"], 1.05)
        self.assertGreater(ratios["clustered"], 2.0)
        self.assertGreater(ratios["shell"], 7.0)

        for row in payload["rows"]:
            with self.subTest(distribution=row["distribution"]):
                rtdl = row["rtdl"]
                cupy = row["cupy"]
                rtdl_summary = rtdl["ranked_aggregate_summary"]
                cupy_summary = cupy["summary"]
                self.assertTrue(rtdl["ok"])
                self.assertEqual(
                    "ranked-summary-aggregate-prepared-query-batch-graph-float32",
                    rtdl["contract"]["mode"],
                )
                self.assertTrue(rtdl["contract"]["prepared_cuda_graph_replay"])
                self.assertTrue(rtdl["claim_boundary"]["prepared_cuda_graph_replay"])
                self.assertFalse(rtdl["claim_boundary"]["rtdl_speedup_claim_authorized"])
                for key in ("bounded_neighbor_count", "nearest_id_checksum", "kth_id_checksum", "row_count"):
                    self.assertEqual(cupy_summary[key], rtdl_summary[key])
                self.assertAlmostEqual(
                    float(cupy_summary["sum_distance"]),
                    float(rtdl_summary["sum_distance"]),
                    delta=max(1.0e-3, abs(float(cupy_summary["sum_distance"])) * 1.0e-6),
                )
                self.assertEqual(0.0, float(rtdl["batch_phase_timings"][-1]["upload"]))

    def test_clean_canonical_harness_confirms_graph_replay_ratios(self) -> None:
        payload = json.loads((ARTIFACT_DIR / "goal2954_clean_rtnn_graph_harness.json").read_text(encoding="utf-8"))

        self.assertEqual("pass", payload["status"])
        self.assertEqual([], payload["source_dirty"])
        self.assertIn("v8.scale65536_repeat9_graph_replay", payload["harness_version"])
        ratios = {row["distribution"]: float(row["cupy_grid_over_rtdl_elapsed_ratio"]) for row in payload["rows"]}
        self.assertGreater(ratios["uniform"], 1.0)
        self.assertGreater(ratios["clustered"], 2.0)
        self.assertGreater(ratios["shell"], 7.0)
        for row in payload["rows"]:
            self.assertEqual("ranked-summary-aggregate-prepared-query-batch-graph-float32", row["contract"]["mode"])
            self.assertTrue(row["ranked_aggregate_matches_cupy_grid"])
            self.assertFalse(row["claim_boundary"]["rtdl_beats_cupy_grid_claim_authorized"])

    def test_report_documents_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2954",
            "route selection",
            "`1.187x`",
            "`2.746x`",
            "`7.241x`",
            "`1.104x`",
            "clean canonical harness",
            "does not add RTNN-specific native code",
            "does not authorize public speedup",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
