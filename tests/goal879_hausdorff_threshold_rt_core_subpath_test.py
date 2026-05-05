from __future__ import annotations

import unittest
from unittest import mock

from examples import rtdl_hausdorff_distance_app as app


class _FakePreparedThreshold:
    def __call__(
        self,
        *,
        search_points,
        query_points,
        radius: float,
        threshold: int,
        backend: str,
        max_radius: float,
        prepare_scene,
    ):
        self.query_count = len(query_points)
        self.radius = radius
        self.threshold = threshold
        self.backend = backend
        self.max_radius = max_radius
        return {
            "primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
            "summary_primitive": "REDUCE_INT(COUNT)",
            "threshold_reached_count": len(query_points),
            "run_phases": {
                "scene_prepare_sec": 0.001,
                "query_fixed_radius_threshold_reached_count_sec": 0.002,
            },
        }


class _PartialPreparedThreshold(_FakePreparedThreshold):
    def __call__(self, **kwargs):
        result = super().__call__(**kwargs)
        result["threshold_reached_count"] = max(0, self.query_count - 1)
        return result


class Goal879HausdorffThresholdRtCoreSubpathTest(unittest.TestCase):
    def test_optix_threshold_summary_matches_oracle_when_radius_covers_fixture(self) -> None:
        fake = _FakePreparedThreshold()
        with mock.patch.object(
            app.rt,
            "run_generic_prepared_fixed_radius_threshold_reached_count_2d",
            side_effect=fake,
        ):
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
        self.assertEqual(payload["directed_a_to_b"]["summary_mode"], "scalar_threshold_count")
        self.assertEqual(payload["directed_a_to_b"]["generic_primitive"], "FIXED_RADIUS_COUNT_THRESHOLD_2D")
        self.assertEqual(payload["directed_a_to_b"]["summary_primitive"], "REDUCE_INT(COUNT)")
        self.assertIsNone(payload["directed_a_to_b"]["row_count"])
        self.assertTrue(payload["directed_a_to_b"]["identity_parity_available"])
        self.assertTrue(payload["oracle_decision_matches"])
        self.assertTrue(payload["oracle_identity_matches"])

    def test_optix_threshold_failure_keeps_scalar_identity_boundary(self) -> None:
        with mock.patch.object(
            app.rt,
            "run_generic_prepared_fixed_radius_threshold_reached_count_2d",
            side_effect=_PartialPreparedThreshold(),
        ):
            payload = app.run_app(
                "optix",
                copies=1,
                optix_summary_mode="directed_threshold_prepared",
                hausdorff_threshold=0.4,
                require_rt_core=True,
            )

        self.assertFalse(payload["within_threshold"])
        self.assertFalse(payload["matches_oracle"])
        self.assertIsNone(payload["directed_a_to_b"]["violating_source_ids"])
        self.assertFalse(payload["directed_a_to_b"]["identity_parity_available"])
        self.assertIsNone(payload["directed_b_to_a"]["violating_source_ids"])
        self.assertFalse(payload["directed_b_to_a"]["identity_parity_available"])
        self.assertIsNone(payload["oracle_identity_matches"])

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
