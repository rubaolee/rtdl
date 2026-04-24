from __future__ import annotations

import unittest
from unittest import mock

from examples import rtdl_hausdorff_distance_app as app


class _FakePreparedThreshold:
    def __init__(self, target, max_radius: float):
        self.target = target
        self.max_radius = max_radius

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def run(self, query_points, *, radius: float, threshold: int):
        return tuple(
            {
                "query_id": point.id,
                "neighbor_count": 1,
                "threshold_reached": 1,
            }
            for point in query_points
        )


class Goal879HausdorffThresholdRtCoreSubpathTest(unittest.TestCase):
    def test_optix_threshold_summary_matches_oracle_when_radius_covers_fixture(self) -> None:
        with mock.patch.object(app.rt, "prepare_optix_fixed_radius_count_threshold_2d", side_effect=_FakePreparedThreshold):
            payload = app.run_app(
                "optix",
                copies=2,
                optix_summary_mode="directed_threshold_prepared",
                hausdorff_threshold=0.4,
                require_rt_core=True,
            )
        self.assertTrue(payload["rt_core_accelerated"])
        self.assertTrue(payload["within_threshold"])
        self.assertTrue(payload["oracle_within_threshold"])
        self.assertTrue(payload["matches_oracle"])
        self.assertIsNone(payload["hausdorff_distance"])

    def test_require_rt_core_rejects_default_knn_rows_mode(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "directed_threshold_prepared"):
            app.run_app("optix", require_rt_core=True)

    def test_threshold_summary_records_violating_sources(self) -> None:
        source = app.make_authored_point_sets(copies=1)["points_a"]
        rows = (
            {"query_id": 1, "neighbor_count": 1, "threshold_reached": 1},
            {"query_id": 2, "neighbor_count": 0, "threshold_reached": 0},
        )
        summary = app._directed_threshold_from_count_rows(
            rows,
            source=source,
            radius=0.1,
            label="a_to_b",
        )
        self.assertFalse(summary["within_threshold"])
        self.assertEqual(summary["violating_source_ids"], [2, 3, 4])

    def test_negative_threshold_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "hausdorff_threshold must be non-negative"):
            app.run_app("optix", optix_summary_mode="directed_threshold_prepared", hausdorff_threshold=-1.0)


if __name__ == "__main__":
    unittest.main()
