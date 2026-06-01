import json
import unittest
from pathlib import Path

from scripts import goal2800_rtnn_v25_live_ranked_summary_harness as rtnn_harness


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2909_rtnn_repeat_stability_2026-05-31.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2909_rtnn_repeat_stability_pod"


def _median(values: list[float]) -> float:
    ordered = sorted(float(value) for value in values)
    return ordered[len(ordered) // 2]


class Goal2909RtnnRepeatStabilityTest(unittest.TestCase):
    def test_rtnn_default_repeat_is_stable_enough_for_short_rows(self) -> None:
        self.assertEqual(rtnn_harness.DEFAULT_REPEAT, 9)
        self.assertIn("repeat9", rtnn_harness.GOAL2800_HARNESS_VERSION)

    def test_repeat9_clustered_probe_beats_cupy_same_contract(self) -> None:
        current = json.loads(
            (ARTIFACT_DIR / "clustered_ranked-summary-aggregate-prepared-query-float32.json").read_text(
                encoding="utf-8"
            )
        )
        graph = json.loads(
            (ARTIFACT_DIR / "clustered_ranked-summary-aggregate-prepared-query-batch-graph-float32.json").read_text(
                encoding="utf-8"
            )
        )
        cupy = json.loads((ARTIFACT_DIR / "clustered_cupy_grid.json").read_text(encoding="utf-8"))

        current_median = _median(current["elapsed_runs_sec"])
        graph_median = _median(graph["elapsed_runs_sec"])
        cupy_median = _median(cupy["elapsed_runs_sec"])

        self.assertTrue(current["ok"])
        self.assertTrue(graph["ok"])
        self.assertTrue(cupy["ok"])
        self.assertEqual(current["ranked_aggregate_summary"]["bounded_neighbor_count"], 1_287_932)
        self.assertEqual(graph["ranked_aggregate_summary"]["bounded_neighbor_count"], 1_287_932)
        self.assertEqual(cupy["summary"]["bounded_neighbor_count"], 1_287_932)
        self.assertLess(current_median, cupy_median)
        self.assertLess(graph_median, cupy_median)
        self.assertGreater(cupy_median / current_median, 2.0)

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("repeat = 9", text)
        self.assertIn("2.65x", text)
        self.assertIn("No native engine code changed", text)
        self.assertIn("not a v2.5 release packet", text)


if __name__ == "__main__":
    unittest.main()
