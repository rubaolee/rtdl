from __future__ import annotations

from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3459_shape_pair_bounds_overlap_area_large_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3459_shape_pair_bounds_overlap_area_large_probe_2026-06-05.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3459_shape_pair_bounds_overlap_area_large_probe_pod_2026-06-05.json"


class Goal3459ShapePairBoundsOverlapAreaLargeProbeTest(unittest.TestCase):
    def test_probe_records_large_scale_continuation_metrics(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "rtdl.goal3459.shape_pair_bounds_overlap_area_large.v1",
            "shape_pair_relation_bounds_overlap_area_cupy",
            "relation_columns_sec",
            "bounds_overlap_area_continuation_sec",
            "all_area_sums_stable",
            "all_nonnegative",
        ):
            self.assertIn(phrase, script)

    def test_report_records_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3459",
            "internal scale/performance characterization",
            "does not compare against the RayJoin paper",
            "does not authorize",
            "exact overlay lane still needs",
        ):
            self.assertIn(phrase, report)

    @unittest.skipUnless(ARTIFACT.exists(), "Goal3459 pod artifact pending")
    def test_pod_artifact_records_stable_large_probe(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.goal3459.shape_pair_bounds_overlap_area_large.v1")
        self.assertEqual(payload["goal"], 3459)
        self.assertEqual(payload["iterations"], 4)
        self.assertTrue(payload["all_row_counts_stable"])
        self.assertTrue(payload["all_group_counts_stable"])
        self.assertTrue(payload["all_nonnegative"])
        self.assertGreater(payload["row_counts"][0], 0)
        self.assertGreater(payload["group_counts"][0], 0)
        self.assertGreaterEqual(payload["bounds_overlap_area_continuation_sec"]["median"], 0.0)
        self.assertTrue(all(value is False for value in payload["claim_boundary"].values()))


if __name__ == "__main__":
    unittest.main()
