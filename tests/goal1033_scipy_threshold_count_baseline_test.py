from __future__ import annotations

import unittest

import rtdsl as rt


class _FakeTree:
    def __init__(self, coords):
        self.coords = tuple(coords)

    def query_ball_point(self, query, r):
        qx, qy = query
        return [
            index
            for index, (x, y) in enumerate(self.coords)
            if ((x - qx) ** 2 + (y - qy) ** 2) ** 0.5 <= r
        ]


class Goal1033ScipyThresholdCountBaselineTest(unittest.TestCase):
    def test_fixed_radius_count_threshold_uses_tree_factory(self) -> None:
        points = (
            rt.Point(id=1, x=0.0, y=0.0),
            rt.Point(id=2, x=0.1, y=0.0),
            rt.Point(id=3, x=2.0, y=0.0),
        )
        rows = rt.run_scipy_fixed_radius_count_threshold(
            points,
            points,
            radius=0.2,
            threshold=2,
            k_max=16,
            tree_factory=_FakeTree,
        )
        self.assertEqual(
            rows,
            (
                {"query_id": 1, "neighbor_count": 2, "threshold_reached": 1},
                {"query_id": 2, "neighbor_count": 2, "threshold_reached": 1},
                {"query_id": 3, "neighbor_count": 1, "threshold_reached": 0},
            ),
        )

    def test_fixed_radius_count_threshold_honors_k_max_cap(self) -> None:
        points = (
            rt.Point(id=1, x=0.0, y=0.0),
            rt.Point(id=2, x=0.1, y=0.0),
            rt.Point(id=3, x=0.2, y=0.0),
        )
        rows = rt.run_scipy_fixed_radius_count_threshold(
            points[:1],
            points,
            radius=1.0,
            threshold=3,
            k_max=2,
            tree_factory=_FakeTree,
        )
        self.assertEqual(rows, ({"query_id": 1, "neighbor_count": 2, "threshold_reached": 0},))

    def test_fixed_radius_count_threshold_rejects_bad_threshold(self) -> None:
        with self.assertRaisesRegex(ValueError, "threshold must be at least 1"):
            rt.run_scipy_fixed_radius_count_threshold(
                (),
                (),
                radius=1.0,
                threshold=0,
                tree_factory=_FakeTree,
            )


if __name__ == "__main__":
    unittest.main()
