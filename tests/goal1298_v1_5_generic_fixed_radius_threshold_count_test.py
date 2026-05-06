from __future__ import annotations

import unittest
from unittest import mock

import rtdsl as rt


class _PreparedFixedRadius:
    enter_count = 0
    exit_count = 0

    def __init__(self, rows=None, scalar_count: int | None = None) -> None:
        self.rows = tuple(rows or ())
        self.scalar_count = scalar_count
        self.run_calls = 0
        self.scalar_calls = 0

    def __enter__(self):
        type(self).enter_count += 1
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        type(self).exit_count += 1

    def run(self, _query_points, *, radius: float, threshold: int = 0):
        self.run_calls += 1
        return self.rows

    def count_threshold_reached(self, _query_points, *, radius: float, threshold: int):
        self.scalar_calls += 1
        if self.scalar_count is None:
            return sum(int(row["threshold_reached"]) for row in self.rows)
        return self.scalar_count


class _PreparedRowsOnlyFixedRadius:
    def __init__(self, rows) -> None:
        self.rows = tuple(rows)
        self.run_calls = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        pass

    def run(self, _query_points, *, radius: float, threshold: int = 0):
        self.run_calls += 1
        return self.rows


class Goal1298V15GenericFixedRadiusThresholdCountTest(unittest.TestCase):
    def setUp(self) -> None:
        _PreparedFixedRadius.enter_count = 0
        _PreparedFixedRadius.exit_count = 0

    def test_cpu_direct_fixed_radius_threshold_count_rows(self) -> None:
        query_points = (
            rt.Point(id=10, x=0.0, y=0.0),
            rt.Point(id=11, x=10.0, y=10.0),
        )
        search_points = (
            rt.Point(id=20, x=0.0, y=0.0),
            rt.Point(id=21, x=0.5, y=0.0),
            rt.Point(id=22, x=10.0, y=10.0),
        )

        result = rt.run_generic_fixed_radius_count_threshold_2d(
            query_points,
            search_points,
            radius=1.0,
            threshold=2,
            backend="cpu",
        )

        self.assertEqual(result["primitive"], "FIXED_RADIUS_COUNT_THRESHOLD_2D")
        self.assertEqual(result["summary_primitive"], "REDUCE_INT(COUNT)")
        self.assertEqual(result["backend"], "cpu")
        self.assertEqual(result["row_count"], 2)
        self.assertEqual(result["threshold_reached_count"], 1)
        self.assertEqual(result["scalar_reduction"]["summary_primitive"], "REDUCE_INT(COUNT)")
        self.assertEqual(result["scalar_reduction"]["result_layout"], "scalar_int64_count")
        self.assertEqual(result["scalar_reduction"]["dtype"], "int64")
        self.assertIsNone(result["scalar_reduction"]["input_field"])
        self.assertIn("not native backend acceleration", result["scalar_reduction"]["claim_boundary"])
        self.assertEqual(
            result["rows"],
            (
                {"query_id": 10, "neighbor_count": 2, "threshold_reached": 1},
                {"query_id": 11, "neighbor_count": 1, "threshold_reached": 0},
            ),
        )
        self.assertIn("query_fixed_radius_count_threshold_sec", result["run_phases"])

    def test_direct_fixed_radius_threshold_count_uses_scalar_reduction_surface(self) -> None:
        query_points = (
            rt.Point(id=10, x=0.0, y=0.0),
            rt.Point(id=11, x=10.0, y=10.0),
        )
        search_points = (
            rt.Point(id=20, x=0.0, y=0.0),
            rt.Point(id=21, x=0.5, y=0.0),
            rt.Point(id=22, x=10.0, y=10.0),
        )

        with mock.patch(
            "rtdsl.generic_primitives.run_generic_scalar_reduction",
            wraps=rt.run_generic_scalar_reduction,
        ) as scalar_reduction:
            result = rt.run_generic_fixed_radius_count_threshold_2d(
                query_points,
                search_points,
                radius=1.0,
                threshold=2,
                backend="cpu",
            )

        scalar_reduction.assert_called_once_with(
            ({"query_id": 10, "neighbor_count": 2, "threshold_reached": 1},),
            summary_primitive="REDUCE_INT(COUNT)",
        )
        self.assertEqual(result["threshold_reached_count"], 1)

    def test_prepared_optix_scalar_count_uses_generic_session(self) -> None:
        prepared = _PreparedFixedRadius(scalar_count=3)

        result = rt.run_generic_prepared_fixed_radius_threshold_reached_count_2d(
            search_points=("search",),
            query_points=("queries",),
            radius=1.0,
            threshold=1,
            backend="optix",
            max_radius=1.0,
            prepare_scene=lambda search_points, *, max_radius: prepared,
        )

        self.assertEqual(result["backend"], "optix")
        self.assertTrue(result["prepared"])
        self.assertTrue(result["scene_reusable"])
        self.assertEqual(result["threshold_reached_count"], 3)
        self.assertEqual(result["query_batch_index"], 1)
        self.assertEqual(prepared.scalar_calls, 1)
        self.assertEqual(_PreparedFixedRadius.enter_count, 1)
        self.assertEqual(_PreparedFixedRadius.exit_count, 1)
        self.assertIn("query_fixed_radius_threshold_reached_count_sec", result["run_phases"])

    def test_prepared_embree_rows_and_scalar_fallback(self) -> None:
        prepared = _PreparedRowsOnlyFixedRadius(
            (
                {"query_id": 1, "neighbor_count": 2, "threshold_reached": 1},
                {"query_id": 2, "neighbor_count": 0, "threshold_reached": 0},
            )
        )

        with rt.prepare_generic_fixed_radius_count_threshold_2d(
            search_points=("search",),
            backend="embree",
            prepare_scene=lambda search_points: prepared,
        ) as session:
            rows_result = session.run(("queries",), radius=1.0, threshold=1)
            scalar_result = session.count_threshold_reached(("queries",), radius=1.0, threshold=1)

        self.assertEqual(rows_result["backend"], "embree")
        self.assertEqual(rows_result["row_count"], 2)
        self.assertEqual(rows_result["threshold_reached_count"], 1)
        self.assertEqual(rows_result["scalar_reduction"]["summary_primitive"], "REDUCE_INT(COUNT)")
        self.assertEqual(scalar_result["threshold_reached_count"], 1)
        self.assertEqual(scalar_result["query_batch_index"], 2)
        self.assertEqual(prepared.run_calls, 2)

    def test_prepared_optix_requires_max_radius(self) -> None:
        with self.assertRaisesRegex(ValueError, "max_radius is required"):
            rt.prepare_generic_fixed_radius_count_threshold_2d(
                search_points=(),
                backend="optix",
                prepare_scene=lambda search_points, *, max_radius: _PreparedFixedRadius(),
            )

    def test_fixed_radius_generic_rejects_frozen_backends(self) -> None:
        for backend in ("vulkan", "hiprt", "apple_rt"):
            with self.subTest(backend=backend):
                with self.assertRaisesRegex(ValueError, "frozen before v2.1"):
                    rt.run_generic_fixed_radius_count_threshold_2d(
                        (),
                        (),
                        radius=1.0,
                        threshold=1,
                        backend=backend,
                    )
                with self.assertRaisesRegex(ValueError, "frozen before v2.1"):
                    rt.prepare_generic_fixed_radius_count_threshold_2d(
                        search_points=(),
                        backend=backend,
                        prepare_scene=lambda search_points: _PreparedFixedRadius(),
                    )

    def test_exports_are_public(self) -> None:
        self.assertIs(rt.GenericPreparedFixedRadiusCountThreshold2D, rt.GenericPreparedFixedRadiusCountThreshold2D)
        self.assertTrue(callable(rt.prepare_generic_fixed_radius_count_threshold_2d))
        self.assertTrue(callable(rt.run_generic_fixed_radius_count_threshold_2d))
        self.assertTrue(callable(rt.run_generic_prepared_fixed_radius_threshold_reached_count_2d))


if __name__ == "__main__":
    unittest.main()
