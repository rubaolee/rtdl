from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt
from rtdsl.simple_polygon_overlay_area_reference import simple_polygon_overlap_area_by_triangulation


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3483_overlay_area_prepared_payload_2026-06-05.md"


class Goal3483OverlayAreaPreparedPayloadTest(unittest.TestCase):
    def test_prepared_payload_triangulates_components_and_records_ranges(self) -> None:
        concave_l = ((0.0, 0.0), (3.0, 0.0), (3.0, 1.0), (1.0, 1.0), (1.0, 3.0), (0.0, 3.0))
        unit_square = ((0.5, 0.5), (2.5, 0.5), (2.5, 2.5), (0.5, 2.5))

        left = rt.prepare_simple_polygon_component_payload((concave_l,), source_shape_ids=(42,))
        right = rt.prepare_simple_polygon_component_payload((unit_square,), source_shape_ids=(7,))
        rows = rt.prepare_overlay_area_pair_rows(left, right, ((0, 0),))

        self.assertEqual(left.component_count, 1)
        self.assertEqual(left.triangle_count, 4)
        self.assertEqual(left.components[0].source_shape_id, 42)
        self.assertEqual(left.components[0].triangle_start, 0)
        self.assertEqual(left.components[0].triangle_stop, 4)
        self.assertEqual(right.triangle_count, 2)
        self.assertEqual(rows[0].left_triangle_count, 4)
        self.assertEqual(rows[0].right_triangle_count, 2)
        self.assertEqual(rows[0].triangle_pair_count, 8)

    def test_prepared_scalar_evaluation_matches_reference_algorithm(self) -> None:
        concave_l = ((0.0, 0.0), (3.0, 0.0), (3.0, 1.0), (1.0, 1.0), (1.0, 3.0), (0.0, 3.0))
        unit_square = ((0.5, 0.5), (2.5, 0.5), (2.5, 2.5), (0.5, 2.5))

        left = rt.prepare_simple_polygon_component_payload((concave_l,))
        right = rt.prepare_simple_polygon_component_payload((unit_square,))
        rows = rt.prepare_overlay_area_pair_rows(left, right, ((0, 0),))
        prepared = rt.evaluate_prepared_overlay_area_scalar(left, right, rows)
        reference = simple_polygon_overlap_area_by_triangulation(concave_l, unit_square)

        self.assertEqual(prepared.positive_row_count, 1)
        self.assertEqual(prepared.triangle_pair_count, reference.triangle_pair_count)
        self.assertAlmostEqual(prepared.total_area, reference.area)
        self.assertAlmostEqual(prepared.total_area, 1.75)

    def test_positive_row_count_uses_policy_threshold_not_clip_epsilon(self) -> None:
        unit_square = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))
        tiny_sliver = ((0.0, 0.0), (5.0e-11, 0.0), (5.0e-11, 1.0), (0.0, 1.0))
        left = rt.prepare_simple_polygon_component_payload((unit_square,))
        right = rt.prepare_simple_polygon_component_payload((tiny_sliver,))
        rows = rt.prepare_overlay_area_pair_rows(left, right, ((0, 0),))

        default_threshold = rt.evaluate_prepared_overlay_area_scalar(left, right, rows)
        explicit_low_threshold = rt.evaluate_prepared_overlay_area_scalar(
            left,
            right,
            rows,
            row_positive_threshold=1.0e-12,
        )

        self.assertGreater(default_threshold.total_area, 1.0e-12)
        self.assertLess(default_threshold.total_area, rt.V2_8_OVERLAY_AREA_ROW_ABS_TOLERANCE)
        self.assertEqual(default_threshold.positive_row_count, 0)
        self.assertEqual(explicit_low_threshold.positive_row_count, 1)

    def test_multi_component_multi_row_pair_payload(self) -> None:
        left_components = (
            ((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)),
            ((10.0, 10.0), (12.0, 10.0), (12.0, 12.0), (10.0, 12.0)),
        )
        right_components = (
            ((1.0, 1.0), (3.0, 1.0), (3.0, 3.0), (1.0, 3.0)),
            ((10.5, 10.5), (11.5, 10.5), (11.5, 11.5), (10.5, 11.5)),
        )
        left = rt.prepare_simple_polygon_component_payload(left_components, source_shape_ids=(100, 101))
        right = rt.prepare_simple_polygon_component_payload(right_components, source_shape_ids=(200, 201))
        rows = rt.prepare_overlay_area_pair_rows(left, right, ((0, 0), (1, 1)))
        prepared = rt.evaluate_prepared_overlay_area_scalar(left, right, rows)

        self.assertEqual(len(rows), 2)
        self.assertEqual([row.triangle_pair_count for row in rows], [4, 4])
        self.assertEqual(prepared.positive_row_count, 2)
        self.assertEqual(prepared.triangle_pair_count, 8)
        self.assertAlmostEqual(prepared.row_areas[0], 1.0)
        self.assertAlmostEqual(prepared.row_areas[1], 1.0)

    def test_invalid_or_degenerate_input_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported_topology_not_canonicalized"):
            rt.prepare_simple_polygon_component_payload((((0.0, 0.0), (1.0, 0.0), (2.0, 0.0)),))

    def test_contract_validation_and_claim_boundary(self) -> None:
        validation = rt.validate_v2_8_overlay_area_prepared_payload_contract()

        self.assertEqual(validation["status"], "accept", validation)
        self.assertEqual(validation["left_triangle_count"], 4)
        self.assertEqual(validation["right_triangle_count"], 2)
        self.assertEqual(validation["triangle_pair_count"], 8)
        self.assertAlmostEqual(validation["fixture_total_area"], 1.75)

        payload = rt.prepare_simple_polygon_component_payload(
            (((0.0, 0.0), (1.0, 0.0), (0.0, 1.0)),)
        )
        metadata = payload.to_metadata()
        for field in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "runtime_kernel_authorized",
        ):
            with self.subTest(field=field):
                self.assertFalse(metadata[field])

    def test_spatial_rayjoin_gap_row_records_prepared_payload(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        spatial = rows["spatial_rayjoin"]

        self.assertIn("prepared simple-polygon component payload", spatial["current_best_path"])
        self.assertIn("flat triangle arrays plus row/component triangle ranges", spatial["current_bottleneck"])
        self.assertIn("Goal3483", spatial["evidence_refs"])
        self.assertFalse(spatial["release_authorized"])
        self.assertFalse(spatial["public_speedup_claim_authorized"])

    def test_report_documents_payload_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "prepared simple polygon component payload",
            "triangle ranges",
            "CPU prototype",
            "fails closed",
            "does not authorize",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
