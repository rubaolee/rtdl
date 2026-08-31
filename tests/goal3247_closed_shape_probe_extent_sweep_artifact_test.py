from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3247_closed_shape_probe_extent_tuning_2026-06-03.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3247_closed_shape_probe_extent_sweep_pod_2026-06-03.json"
STDOUT = ROOT / "docs" / "reports" / "goal3247_closed_shape_probe_extent_sweep_pod_2026-06-03.stdout"


def _result(data: dict, extent: str) -> dict:
    return {row["extent"]: row for row in data["results"]}[extent]


class Goal3247ClosedShapeProbeExtentSweepArtifactTest(unittest.TestCase):
    def test_report_records_best_safe_extent_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Closed-Shape Probe Extent Tuning",
            "RTDL_OPTIX_POINT_PRIMITIVE_QUERY_HALF_EXTENT",
            "default (`0.5`)",
            "0.936108 ms",
            "1.23x",
            "4.84x slower than RayJoin",
            "rejected: misses hits",
            "not \"make `0.25` universal.\"",
            "device-resident grouped ray/segment parity/count",
            "does not authorize release",
            "paper-reproduction claims",
        ):
            self.assertIn(phrase, text)

    def test_artifact_is_clean_and_claim_bounded(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["schema"], "rtdl.goal3247.closed_shape_probe_extent_sweep.v1")
        self.assertEqual(data["commit"], "dfd23f7d15999b8faf775b59cb869c104999aa2d")
        self.assertEqual(data["source_dirty"], [])
        self.assertTrue(all(value is False for value in data["claim_boundary"].values()))
        self.assertEqual(data["summary"]["expected_count_from_default"], 1430)
        self.assertEqual(data["summary"]["best_matching_extent"], "0.25")
        self.assertGreater(data["summary"]["best_matching_speedup_over_default"], 1.2)

    def test_count_preserving_and_rejected_extents_are_visible(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        default = _result(data, "default")
        tuned = _result(data, "0.25")
        near_miss = _result(data, "0.225")

        self.assertEqual(default["summary"]["counts"], [1430] * 5)
        self.assertEqual(tuned["summary"]["counts"], [1430] * 5)
        self.assertEqual(near_miss["summary"]["counts"], [0] * 5)
        self.assertLess(
            tuned["summary"]["prepared_query_ms_median"],
            default["summary"]["prepared_query_ms_median"],
        )
        self.assertLess(
            tuned["summary"]["phase_medians_ms"]["candidate_write_pass"],
            default["summary"]["phase_medians_ms"]["candidate_write_pass"],
        )

    def test_stdout_contains_progress_for_decision_extents(self) -> None:
        text = STDOUT.read_text(encoding="utf-8")

        for phrase in (
            "[goal3247] extent default start",
            "[goal3247] extent 0.25 count=1430",
            "[goal3247] extent 0.225 count=0",
            "goal3247_closed_shape_probe_extent_sweep_pod_2026-06-03.json",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
