from __future__ import annotations

import unittest
from unittest import mock

from examples import rtdl_dbscan_clustering_app as dbscan
from examples import rtdl_outlier_detection_app as outlier


class Goal1301OutlierDbscanGenericMigrationTest(unittest.TestCase):
    def test_outlier_direct_optix_summary_uses_generic_fixed_radius_threshold(self) -> None:
        rows = tuple(
            {
                "query_id": row["point_id"],
                "neighbor_count": min(int(row["neighbor_count"]), outlier.MIN_NEIGHBORS_INCLUDING_SELF),
                "threshold_reached": 0 if bool(row["is_outlier"]) else 1,
            }
            for row in outlier.expected_tiled_density_rows(copies=1)
        )

        with mock.patch.object(
            outlier.rt,
            "run_generic_fixed_radius_count_threshold_2d",
            return_value={
                "primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
                "summary_primitive": "REDUCE_INT(COUNT)",
                "rows": rows,
            },
        ) as run_generic:
            payload = outlier.run_app("optix", optix_summary_mode="rt_count_threshold")

        self.assertTrue(payload["matches_oracle"])
        run_generic.assert_called_once()
        self.assertEqual(run_generic.call_args.kwargs["backend"], "optix")
        self.assertEqual(run_generic.call_args.kwargs["threshold"], outlier.MIN_NEIGHBORS_INCLUDING_SELF)

    def test_outlier_prepared_scalar_uses_generic_fixed_radius_threshold(self) -> None:
        with mock.patch.object(
            outlier.rt,
            "run_generic_prepared_fixed_radius_threshold_reached_count_2d",
            return_value={
                "primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
                "summary_primitive": "REDUCE_INT(COUNT)",
                "threshold_reached_count": 6,
            },
        ) as run_generic:
            payload = outlier.run_app(
                "optix",
                optix_summary_mode="rt_count_threshold_prepared",
                output_mode="density_count",
            )

        self.assertTrue(payload["matches_oracle"])
        self.assertEqual(payload["outlier_count"], 2)
        self.assertEqual(payload["summary_mode"], "scalar_threshold_count")
        run_generic.assert_called_once()
        self.assertEqual(run_generic.call_args.kwargs["backend"], "optix")

    def test_dbscan_direct_optix_summary_uses_generic_fixed_radius_threshold(self) -> None:
        rows = tuple(
            {
                "query_id": row["point_id"],
                "neighbor_count": min(int(row["neighbor_count"]), dbscan.MIN_POINTS),
                "threshold_reached": 1 if bool(row["is_core"]) else 0,
            }
            for row in dbscan.expected_tiled_core_flag_rows(copies=1)
        )

        with mock.patch.object(
            dbscan.rt,
            "run_generic_fixed_radius_count_threshold_2d",
            return_value={
                "primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
                "summary_primitive": "REDUCE_INT(COUNT)",
                "rows": rows,
            },
        ) as run_generic:
            payload = dbscan.run_app("optix", optix_summary_mode="rt_core_flags")

        self.assertTrue(payload["matches_oracle"])
        run_generic.assert_called_once()
        self.assertEqual(run_generic.call_args.kwargs["backend"], "optix")
        self.assertEqual(run_generic.call_args.kwargs["threshold"], dbscan.MIN_POINTS)

    def test_dbscan_prepared_scalar_uses_generic_fixed_radius_threshold(self) -> None:
        with mock.patch.object(
            dbscan.rt,
            "run_generic_prepared_fixed_radius_threshold_reached_count_2d",
            return_value={
                "primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
                "summary_primitive": "REDUCE_INT(COUNT)",
                "threshold_reached_count": 7,
            },
        ) as run_generic:
            payload = dbscan.run_app(
                "optix",
                optix_summary_mode="rt_core_flags_prepared",
                output_mode="core_count",
            )

        self.assertTrue(payload["matches_oracle"])
        self.assertEqual(payload["core_count"], 7)
        self.assertEqual(payload["summary_mode"], "scalar_threshold_count")
        run_generic.assert_called_once()
        self.assertEqual(run_generic.call_args.kwargs["backend"], "optix")


if __name__ == "__main__":
    unittest.main()
