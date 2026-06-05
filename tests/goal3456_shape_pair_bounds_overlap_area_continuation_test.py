from __future__ import annotations

from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "src" / "rtdsl" / "geometry_relation_continuations.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
SCRIPT = ROOT / "scripts" / "goal3456_shape_pair_bounds_overlap_area_continuation_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3456_shape_pair_bounds_overlap_area_continuation_2026-06-05.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3456_shape_pair_bounds_overlap_area_continuation_pod_2026-06-05.json"


class Goal3456ShapePairBoundsOverlapAreaContinuationTest(unittest.TestCase):
    def test_generic_cupy_continuation_consumes_ordinals_and_geometry_payload(self) -> None:
        module = MODULE.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")

        for phrase in (
            "shape_pair_relation_bounds_overlap_area_cupy",
            "as_cupy_ordinal_columns",
            "as_cupy_geometry_payload_columns",
            "axis_aligned_bounds_overlap_area_upper_bound",
            '"exact_polygon_overlay_area": False',
            '"full_overlay_area_claim_authorized": False',
        ):
            self.assertIn(phrase, module)
        self.assertIn("shape_pair_relation_bounds_overlap_area_cupy", init)

    def test_probe_and_report_record_boundaries(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "rtdl.goal3456.shape_pair_bounds_overlap_area_continuation.v1",
            "rows_match",
            "group_sums_match",
            "shape_pair_relation_bounds_overlap_area_cupy",
        ):
            self.assertIn(phrase, script)

        for phrase in (
            "Goal3456",
            "bounds-overlap area",
            "not exact polygon overlay area",
            "does not authorize",
            "Full RayJoin-style overlay still requires",
        ):
            self.assertIn(phrase, report)

    @unittest.skipUnless(ARTIFACT.exists(), "Goal3456 pod artifact pending")
    def test_pod_artifact_bounds_overlap_area_matches_fixture(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.goal3456.shape_pair_bounds_overlap_area_continuation.v1")
        self.assertEqual(payload["goal"], 3456)
        self.assertTrue(payload["rows_match"])
        self.assertTrue(payload["group_sums_match"])
        self.assertEqual(payload["observed_rows"], payload["expected_rows"])
        self.assertEqual(payload["observed_group_sums"], payload["expected_group_sums"])
        self.assertEqual(
            payload["continuation_metadata"]["area_semantics"],
            "axis_aligned_bounds_overlap_area_upper_bound",
        )
        self.assertFalse(payload["continuation_metadata"]["exact_polygon_overlay_area"])
        self.assertTrue(all(value is False for value in payload["claim_boundary"].values()))


if __name__ == "__main__":
    unittest.main()
