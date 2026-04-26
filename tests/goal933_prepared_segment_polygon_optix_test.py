from __future__ import annotations

import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal933PreparedSegmentPolygonOptixTest(unittest.TestCase):
    def test_empty_prepared_polygon_scene_returns_zero_hit_counts_without_native_library(self) -> None:
        with rt.prepare_optix_segment_polygon_hitcount_2d(()) as prepared:
            rows = prepared.run((rt.Segment(7, 0.0, 0.0, 1.0, 1.0),))

        self.assertEqual(rows, ({"segment_id": 7, "hit_count": 0},))

    def test_empty_prepared_polygon_scene_counts_threshold_without_native_library(self) -> None:
        with rt.prepare_optix_segment_polygon_hitcount_2d(()) as prepared:
            self.assertEqual(
                prepared.count_at_least((rt.Segment(7, 0.0, 0.0, 1.0, 1.0),), threshold=1),
                0,
            )
            self.assertEqual(
                prepared.count_at_least((rt.Segment(7, 0.0, 0.0, 1.0, 1.0),), threshold=0),
                1,
            )

    def test_empty_prepared_polygon_scene_aggregates_without_native_library(self) -> None:
        with rt.prepare_optix_segment_polygon_hitcount_2d(()) as prepared:
            self.assertEqual(
                prepared.aggregate((rt.Segment(7, 0.0, 0.0, 1.0, 1.0),), positive_threshold=1),
                {"row_count": 1, "hit_sum": 0, "positive_count": 0},
            )
            self.assertEqual(
                prepared.aggregate((rt.Segment(7, 0.0, 0.0, 1.0, 1.0),), positive_threshold=0),
                {"row_count": 1, "hit_sum": 0, "positive_count": 1},
            )

    def test_prepared_polygon_threshold_count_validates_threshold(self) -> None:
        with rt.prepare_optix_segment_polygon_hitcount_2d(()) as prepared:
            with self.assertRaisesRegex(ValueError, "threshold must be non-negative"):
                prepared.count_at_least((), threshold=-1)
            with self.assertRaisesRegex(ValueError, "positive_threshold must be non-negative"):
                prepared.aggregate((), positive_threshold=-1)

    def test_closed_prepared_scene_is_rejected(self) -> None:
        prepared = rt.prepare_optix_segment_polygon_hitcount_2d(())
        prepared.close()

        with self.assertRaisesRegex(RuntimeError, "handle is closed"):
            prepared.run((rt.Segment(1, 0.0, 0.0, 1.0, 1.0),))
        with self.assertRaisesRegex(RuntimeError, "handle is closed"):
            prepared.count_at_least((rt.Segment(1, 0.0, 0.0, 1.0, 1.0),), threshold=1)
        with self.assertRaisesRegex(RuntimeError, "handle is closed"):
            prepared.aggregate((rt.Segment(1, 0.0, 0.0, 1.0, 1.0),), positive_threshold=1)

    def test_empty_prepared_pair_row_scene_returns_metadata_without_native_library(self) -> None:
        with rt.prepare_optix_segment_polygon_anyhit_rows_2d(()) as prepared:
            result = prepared.run_with_metadata(
                (rt.Segment(7, 0.0, 0.0, 1.0, 1.0),),
                output_capacity=4,
            )

        self.assertEqual(result["rows"], ())
        self.assertEqual(result["emitted_count"], 0)
        self.assertEqual(result["copied_count"], 0)
        self.assertFalse(result["overflowed"])

    def test_closed_prepared_pair_row_scene_is_rejected(self) -> None:
        prepared = rt.prepare_optix_segment_polygon_anyhit_rows_2d(())
        prepared.close()

        with self.assertRaisesRegex(RuntimeError, "handle is closed"):
            prepared.run((rt.Segment(1, 0.0, 0.0, 1.0, 1.0),), output_capacity=4)

    def test_pair_row_output_capacity_must_be_positive(self) -> None:
        with rt.prepare_optix_segment_polygon_anyhit_rows_2d(()) as prepared:
            with self.assertRaisesRegex(ValueError, "output_capacity must be positive"):
                prepared.run((rt.Segment(1, 0.0, 0.0, 1.0, 1.0),), output_capacity=0)

    def test_native_sources_export_prepared_segment_polygon_abi(self) -> None:
        prelude = (ROOT / "src/native/optix/rtdl_optix_prelude.h").read_text(encoding="utf-8")
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text(encoding="utf-8")
        workloads = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(encoding="utf-8")

        self.assertIn("rtdl_optix_prepare_segment_polygon_hitcount_2d", prelude)
        self.assertIn("rtdl_optix_run_prepared_segment_polygon_hitcount_2d", prelude)
        self.assertIn("rtdl_optix_count_prepared_segment_polygon_hitcount_at_least_2d", prelude)
        self.assertIn("rtdl_optix_aggregate_prepared_segment_polygon_hitcount_2d", prelude)
        self.assertIn("rtdl_optix_destroy_prepared_segment_polygon_hitcount_2d", prelude)
        self.assertIn("rtdl_optix_prepare_segment_polygon_anyhit_rows_2d", prelude)
        self.assertIn("rtdl_optix_run_prepared_segment_polygon_anyhit_rows_2d", prelude)
        self.assertIn("rtdl_optix_destroy_prepared_segment_polygon_anyhit_rows_2d", prelude)
        self.assertIn("PreparedSegmentPolygonHitcount2D", workloads)
        self.assertIn("prepare_segment_polygon_hitcount_2d_optix", workloads)
        self.assertIn("run_prepared_segment_polygon_hitcount_2d_optix", workloads)
        self.assertIn("count_prepared_segment_polygon_hitcount_at_least_2d_optix", workloads)
        self.assertIn("aggregate_prepared_segment_polygon_hitcount_2d_optix", workloads)
        self.assertIn("PreparedSegmentPolygonAnyhitRows2D", workloads)
        self.assertIn("prepare_segment_polygon_anyhit_rows_2d_optix", workloads)
        self.assertIn("run_prepared_segment_polygon_anyhit_rows_2d_optix", workloads)
        self.assertIn("rtdl_optix_prepare_segment_polygon_hitcount_2d", api)
        self.assertIn("rtdl_optix_run_prepared_segment_polygon_hitcount_2d", api)
        self.assertIn("rtdl_optix_count_prepared_segment_polygon_hitcount_at_least_2d", api)
        self.assertIn("rtdl_optix_aggregate_prepared_segment_polygon_hitcount_2d", api)
        self.assertIn("rtdl_optix_destroy_prepared_segment_polygon_hitcount_2d", api)
        self.assertIn("rtdl_optix_prepare_segment_polygon_anyhit_rows_2d", api)
        self.assertIn("rtdl_optix_run_prepared_segment_polygon_anyhit_rows_2d", api)
        self.assertIn("rtdl_optix_destroy_prepared_segment_polygon_anyhit_rows_2d", api)

    def test_python_runtime_exports_prepared_segment_polygon_api(self) -> None:
        self.assertTrue(hasattr(rt, "prepare_optix_segment_polygon_hitcount_2d"))
        self.assertTrue(hasattr(rt, "PreparedOptixSegmentPolygonHitcount2D"))
        self.assertTrue(hasattr(rt, "prepare_optix_segment_polygon_anyhit_rows_2d"))
        self.assertTrue(hasattr(rt, "PreparedOptixSegmentPolygonAnyHitRows2D"))


if __name__ == "__main__":
    unittest.main()
