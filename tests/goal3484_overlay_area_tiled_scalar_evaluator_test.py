from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3484_overlay_area_tiled_scalar_evaluator_2026-06-05.md"


def _fixture_payloads():
    concave_l = ((0.0, 0.0), (3.0, 0.0), (3.0, 1.0), (1.0, 1.0), (1.0, 3.0), (0.0, 3.0))
    square = ((0.5, 0.5), (2.5, 0.5), (2.5, 2.5), (0.5, 2.5))
    left = rt.prepare_simple_polygon_component_payload((concave_l,))
    right = rt.prepare_simple_polygon_component_payload((square,))
    rows = rt.prepare_overlay_area_pair_rows(left, right, ((0, 0),))
    return left, right, rows


class Goal3484OverlayAreaTiledScalarEvaluatorTest(unittest.TestCase):
    def test_tiled_evaluator_matches_untiled_scalar_reference(self) -> None:
        left, right, rows = _fixture_payloads()

        untiled = rt.evaluate_prepared_overlay_area_scalar(left, right, rows)
        tiled = rt.evaluate_prepared_overlay_area_scalar_tiled(
            left,
            right,
            rows,
            max_triangle_pairs_per_tile=3,
        )

        self.assertAlmostEqual(tiled.total_area, untiled.total_area)
        self.assertEqual(tiled.row_areas, untiled.row_areas)
        self.assertEqual(tiled.triangle_pair_count, untiled.triangle_pair_count)
        self.assertEqual(tiled.tile_count, 3)
        self.assertLessEqual(tiled.max_observed_tile_pairs, 3)
        self.assertTrue(tiled.completed_without_truncation)

    def test_tiled_evaluator_can_stream_one_triangle_pair_at_a_time(self) -> None:
        left, right, rows = _fixture_payloads()

        tiled = rt.evaluate_prepared_overlay_area_scalar_tiled(
            left,
            right,
            rows,
            max_triangle_pairs_per_tile=1,
        )

        self.assertEqual(tiled.triangle_pair_count, 8)
        self.assertEqual(tiled.tile_count, 8)
        self.assertEqual(tiled.max_observed_tile_pairs, 1)
        self.assertAlmostEqual(tiled.total_area, 1.75)

    def test_tiled_positive_row_count_uses_policy_threshold(self) -> None:
        unit_square = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))
        tiny_sliver = ((0.0, 0.0), (5.0e-11, 0.0), (5.0e-11, 1.0), (0.0, 1.0))
        left = rt.prepare_simple_polygon_component_payload((unit_square,))
        right = rt.prepare_simple_polygon_component_payload((tiny_sliver,))
        rows = rt.prepare_overlay_area_pair_rows(left, right, ((0, 0),))

        default_threshold = rt.evaluate_prepared_overlay_area_scalar_tiled(
            left,
            right,
            rows,
            max_triangle_pairs_per_tile=2,
        )
        explicit_low_threshold = rt.evaluate_prepared_overlay_area_scalar_tiled(
            left,
            right,
            rows,
            max_triangle_pairs_per_tile=2,
            row_positive_threshold=1.0e-12,
        )

        self.assertGreater(default_threshold.total_area, 1.0e-12)
        self.assertLess(default_threshold.total_area, rt.V2_8_OVERLAY_AREA_ROW_ABS_TOLERANCE)
        self.assertEqual(default_threshold.positive_row_count, 0)
        self.assertEqual(explicit_low_threshold.positive_row_count, 1)

    def test_tiled_evaluator_rejects_invalid_scratch_capacity(self) -> None:
        left, right, rows = _fixture_payloads()

        with self.assertRaisesRegex(ValueError, "scratch capacity must fail closed"):
            rt.evaluate_prepared_overlay_area_scalar_tiled(
                left,
                right,
                rows,
                max_triangle_pairs_per_tile=0,
            )

    def test_contract_validation_records_tiled_fields(self) -> None:
        validation = rt.validate_v2_8_overlay_area_prepared_payload_contract()

        self.assertEqual(validation["status"], "accept", validation)
        self.assertEqual(validation["tiled_tile_count"], 3)
        self.assertEqual(validation["tiled_max_observed_tile_pairs"], 3)

    def test_tiled_metadata_blocks_claims(self) -> None:
        left, right, rows = _fixture_payloads()
        tiled = rt.evaluate_prepared_overlay_area_scalar_tiled(
            left,
            right,
            rows,
            max_triangle_pairs_per_tile=4,
        )
        metadata = tiled.to_metadata()

        self.assertEqual(metadata["algorithm"], "prepared_component_triangle_pair_tiled_convex_clip")
        self.assertTrue(metadata["completed_without_truncation"])
        for field in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "runtime_kernel_authorized",
        ):
            with self.subTest(field=field):
                self.assertFalse(metadata[field])

    def test_spatial_rayjoin_gap_row_records_tiled_evaluator(self) -> None:
        rows = {row["benchmark_app"]: row for row in rt.v2_8_benchmark_runtime_gap_matrix()}
        spatial = rows["spatial_rayjoin"]

        self.assertIn("bounded tiled CPU evaluator", spatial["current_best_path"])
        self.assertIn("no silent triangle-pair truncation", spatial["current_bottleneck"])
        self.assertIn("Goal3484", spatial["evidence_refs"])
        self.assertFalse(spatial["release_authorized"])

    def test_report_documents_tiled_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "bounded triangle-pair tiles",
            "completed_without_truncation",
            "scratch capacity must fail closed",
            "CPU evaluator",
            "does not authorize",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
