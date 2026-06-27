from __future__ import annotations

from dataclasses import dataclass
import unittest

import rtdsl as rt
from examples.benchmark_apps.spatial_rayjoin import (
    rtdl_rayjoin_v2_spatial_join_app as rayjoin_app,
)


@dataclass(frozen=True)
class ProbePoint:
    id: int
    x: float
    y: float


class Goal3280SpatialOrderPoints2DGenericHelperTest(unittest.TestCase):
    def test_generic_axis_orders_preserve_ids(self) -> None:
        points = (
            ProbePoint(30, 2.0, 0.0),
            ProbePoint(10, 1.0, 3.0),
            ProbePoint(20, 1.0, 2.0),
        )

        ordered = rt.spatial_order_points_2d(points, "x_then_y")

        self.assertEqual([point.id for point in ordered], [20, 10, 30])
        self.assertEqual(sorted(point.id for point in ordered), [10, 20, 30])

    def test_generic_morton_order_is_deterministic(self) -> None:
        points = (
            {"id": 4, "x": 1.0, "y": 1.0},
            {"id": 1, "x": 0.0, "y": 0.0},
            {"id": 3, "x": 1.0, "y": 0.0},
            {"id": 2, "x": 0.0, "y": 1.0},
        )

        first = rt.spatial_order_points_2d(points, "morton_xy")
        second = rt.spatial_order_points_2d(points, "morton_xy")

        self.assertEqual([point["id"] for point in first], [1, 3, 2, 4])
        self.assertEqual([point["id"] for point in first], [point["id"] for point in second])

    def test_rayjoin_locality_wrapper_delegates_to_generic_helper(self) -> None:
        points = (
            {"id": 4, "x": 1.0, "y": 1.0},
            {"id": 1, "x": 0.0, "y": 0.0},
            {"id": 3, "x": 1.0, "y": 0.0},
            {"id": 2, "x": 0.0, "y": 1.0},
        )

        self.assertEqual(
            rayjoin_app._order_points_for_locality(points, "morton_xy"),
            rt.spatial_order_points_2d(points, "morton_xy"),
        )

    def test_discovery_exposes_spatial_order_without_app_language(self) -> None:
        matches = rt.find_primitive(text="morton order points before packing")

        self.assertTrue(matches)
        self.assertEqual(matches[0].node_id, "execution.spatial_order_points_2d")
        description = rt.describe_primitive("execution.spatial_order_points_2d")
        self.assertIn("intent:order", description["capability_tags"])
        self.assertNotIn("rayjoin", " ".join(description["aliases"]).lower())

    def test_invalid_mode_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "mode must be one of"):
            rt.spatial_order_points_2d((), "bad_mode")


if __name__ == "__main__":
    unittest.main()
