from __future__ import annotations

import unittest
from unittest import mock

import numpy as np

from examples.v2_0.research_benchmarks.hausdorff_xhd import rtdl_hausdorff_v2_function as hd


class _FakePointGroupPrepared:
    def __init__(self, captured: dict[str, float], source_id: int, target_id: int) -> None:
        self._captured = captured
        self._source_id = source_id
        self._target_id = target_id

    def __enter__(self) -> "_FakePointGroupPrepared":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def nearest_max_distance_row(self, query_points, *, radius: float) -> dict[str, object]:
        self._captured["query_radius"] = float(radius)
        return {"query_id": self._source_id, "neighbor_id": self._target_id, "distance": 0.0}


class Goal2924HausdorffPreparedRadiusGuardTest(unittest.TestCase):
    def test_prepared_radius_guard_adds_native_rounding_slack(self) -> None:
        self.assertEqual(0.0, hd._prepared_radius_guard(0.0))
        self.assertGreater(hd._prepared_radius_guard(1.0), 1.0)

    def test_grouped_reduced_query_uses_exact_upper_bound_but_prepares_guarded_radius(self) -> None:
        source = {
            "ids": np.asarray([101, 102], dtype=np.int64),
            "x": np.asarray([0.0, 2.0], dtype=np.float64),
            "y": np.asarray([0.0, 0.0], dtype=np.float64),
        }
        target = {
            "ids": np.asarray([201, 202], dtype=np.int64),
            "x": np.asarray([0.5, 3.0], dtype=np.float64),
            "y": np.asarray([0.0, 0.0], dtype=np.float64),
        }
        upper_bound = hd._point_set_upper_bound(source, target)
        captured: dict[str, float] = {}

        def fake_prepare(search_points, groups, *, max_radius: float):
            captured["prepared_max_radius"] = float(max_radius)
            return _FakePointGroupPrepared(captured, source_id=101, target_id=201)

        with mock.patch("rtdsl.optix_runtime.prepare_optix_point_group_nearest_witness_2d", fake_prepare):
            result = hd._directed_rt_grouped_reduced_nearest_witness(
                source,
                target,
                upper_bound=upper_bound,
                radius=None,
                seed_with_threshold=False,
                threshold_tolerance=1.0e-4,
                threshold_max_iterations=1,
                target_points_per_group=4096,
            )

        self.assertEqual(upper_bound, captured["query_radius"])
        self.assertGreater(captured["prepared_max_radius"], captured["query_radius"])
        self.assertEqual("point_group_nearest_max_distance", result["native_reduction"])
        self.assertEqual(4096, result["target_points_per_group"])


if __name__ == "__main__":
    unittest.main()
