from __future__ import annotations

from dataclasses import dataclass
import unittest

from examples.current.research_benchmarks.spatial_rayjoin import (
    rtdl_rayjoin_v2_spatial_join_app as rayjoin_app,
)


@dataclass(frozen=True)
class ProbePoint:
    id: int
    x: float
    y: float


class Goal3278RayJoinPipPointOrderLocalityProbeTest(unittest.TestCase):
    def test_x_then_y_order_preserves_caller_ids(self) -> None:
        points = (
            ProbePoint(30, 2.0, 0.0),
            ProbePoint(10, 1.0, 3.0),
            ProbePoint(20, 1.0, 2.0),
        )

        ordered = rayjoin_app._order_points_for_locality(points, "x_then_y")

        self.assertEqual([point.id for point in ordered], [20, 10, 30])
        self.assertEqual(sorted(point.id for point in ordered), [10, 20, 30])

    def test_morton_order_is_deterministic_and_id_stable(self) -> None:
        points = (
            {"id": 4, "x": 1.0, "y": 1.0},
            {"id": 1, "x": 0.0, "y": 0.0},
            {"id": 3, "x": 1.0, "y": 0.0},
            {"id": 2, "x": 0.0, "y": 1.0},
        )

        first = rayjoin_app._order_points_for_locality(points, "morton_xy")
        second = rayjoin_app._order_points_for_locality(points, "morton_xy")

        self.assertEqual([point["id"] for point in first], [1, 3, 2, 4])
        self.assertEqual([point["id"] for point in first], [point["id"] for point in second])

    def test_invalid_point_order_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "point_order_mode"):
            rayjoin_app._order_points_for_locality((), "bad_mode")

    def test_app_rejects_non_pip_point_order(self) -> None:
        with self.assertRaisesRegex(ValueError, "only valid for PIP"):
            rayjoin_app.run_rayjoin_prepared_optix_workload(
                "lsi",
                dataset="tests/fixtures/rayjoin/br_county_subset.cdb + tests/fixtures/rayjoin/br_soil_subset.cdb",
                point_order_mode="morton_xy",
            )


if __name__ == "__main__":
    unittest.main()
