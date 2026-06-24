from __future__ import annotations

import unittest
from unittest import mock

from examples import rtdl_hausdorff_distance_app as app


class _FakePreparedThreshold:
    def __call__(
        self,
        *,
        search_points,
        backend: str,
        max_radius: float,
    ):
        self.search_points = search_points
        self.backend = backend
        self.max_radius = max_radius
        self.scene_prepare_sec = 0.001
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def count_threshold_reached(self, query_points, *, radius: float, threshold: int):
        self.query_count = len(query_points)
        self.radius = radius
        self.threshold = threshold
        return {
            "primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
            "summary_primitive": "REDUCE_INT(COUNT)",
            "backend": self.backend,
            "prepared": True,
            "scene_reusable": True,
            "threshold_reached_count": len(query_points),
            "result_layout": "aggregate_threshold_reached_count",
            "native_scalar_count_used": True,
            "threshold_summary_rows_materialized_on_host": False,
            "hot_path_host_materialization": False,
            "prepared_search_structure_resident_between_rtdl_phases": True,
            "query_points_device_resident_between_rtdl_phases": False,
            "internal_device_residency_between_rtdl_phases": True,
            "internal_residency_scope": "prepared_search_structure_only_query_points_not_device_resident",
            "run_phases": {
                "scene_prepare_sec": 0.001,
                "query_fixed_radius_threshold_reached_count_sec": 0.002,
            },
        }


class _PartialPreparedThreshold(_FakePreparedThreshold):
    def count_threshold_reached(self, *args, **kwargs):
        result = super().count_threshold_reached(*args, **kwargs)
        result["threshold_reached_count"] = max(0, self.query_count - 1)
        return result


class Goal879HausdorffThresholdRtCoreSubpathTest(unittest.TestCase):
    def test_optix_threshold_summary_matches_oracle_when_radius_covers_fixture(self) -> None:
        fake = _FakePreparedThreshold()
        with mock.patch.object(
            app.rt,
            "prepare_generic_fixed_radius_count_threshold_2d",
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
            "prepare_generic_fixed_radius_count_threshold_2d",
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
