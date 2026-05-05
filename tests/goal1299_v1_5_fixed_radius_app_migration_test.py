from __future__ import annotations

import unittest
from unittest import mock

from examples import rtdl_event_hotspot_screening as hotspot
from examples import rtdl_service_coverage_gaps as coverage


class Goal1299V15FixedRadiusAppMigrationTest(unittest.TestCase):
    def test_service_coverage_optix_summary_uses_generic_prepared_wrapper(self) -> None:
        with mock.patch.object(
            coverage.rt,
            "run_generic_prepared_fixed_radius_threshold_reached_count_2d",
            return_value={
                "primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
                "summary_primitive": "REDUCE_INT(COUNT)",
                "threshold_reached_count": 3,
            },
        ) as generic_count:
            payload = coverage.run_case("optix", optix_summary_mode="gap_summary_prepared")

        generic_count.assert_called_once()
        _, kwargs = generic_count.call_args
        self.assertEqual(kwargs["backend"], "optix")
        self.assertEqual(kwargs["radius"], coverage.RADIUS)
        self.assertEqual(kwargs["threshold"], 1)
        self.assertEqual(payload["covered_household_count"], 3)
        self.assertEqual(payload["summary_boundary"], (
            "gap_summary_prepared reports only scalar covered/uncovered counts; use rows mode "
            "when household ids, clinic ids, distances, or clinic loads are required."
        ))

    def test_service_coverage_embree_summary_uses_generic_direct_wrapper(self) -> None:
        with mock.patch.object(
            coverage.rt,
            "run_generic_fixed_radius_count_threshold_2d",
            return_value={
                "rows": (
                    {"query_id": 1, "neighbor_count": 1, "threshold_reached": 1},
                    {"query_id": 2, "neighbor_count": 0, "threshold_reached": 0},
                )
            },
        ) as generic_rows:
            payload = coverage.run_case("embree", embree_summary_mode="gap_summary")

        generic_rows.assert_called_once()
        _, kwargs = generic_rows.call_args
        self.assertEqual(kwargs["backend"], "embree")
        self.assertEqual(kwargs["threshold"], 1)
        self.assertEqual(payload["covered_household_count"], 1)
        self.assertEqual(payload["uncovered_household_ids"], [2, 3, 4])

    def test_event_hotspot_optix_summary_uses_generic_prepared_wrapper(self) -> None:
        with mock.patch.object(
            hotspot.rt,
            "run_generic_prepared_fixed_radius_threshold_reached_count_2d",
            return_value={
                "primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
                "summary_primitive": "REDUCE_INT(COUNT)",
                "threshold_reached_count": 4,
            },
        ) as generic_count:
            payload = hotspot.run_case("optix", optix_summary_mode="count_summary_prepared")

        generic_count.assert_called_once()
        _, kwargs = generic_count.call_args
        self.assertEqual(kwargs["backend"], "optix")
        self.assertEqual(kwargs["radius"], hotspot.RADIUS)
        self.assertEqual(kwargs["threshold"], hotspot.HOTSPOT_THRESHOLD + 1)
        self.assertEqual(payload["hotspot_count"], 4)
        self.assertIsNone(payload["hotspots"])

    def test_event_hotspot_embree_summary_uses_generic_direct_wrapper(self) -> None:
        with mock.patch.object(
            hotspot.rt,
            "run_generic_fixed_radius_count_threshold_2d",
            return_value={
                "rows": (
                    {"query_id": 1, "neighbor_count": 4, "threshold_reached": 0},
                    {"query_id": 2, "neighbor_count": 1, "threshold_reached": 0},
                )
            },
        ) as generic_rows:
            payload = hotspot.run_case("embree", embree_summary_mode="count_summary")

        generic_rows.assert_called_once()
        _, kwargs = generic_rows.call_args
        self.assertEqual(kwargs["backend"], "embree")
        self.assertEqual(kwargs["threshold"], 0)
        self.assertEqual(payload["hotspot_count"], 1)
        self.assertEqual(payload["summary_rows"], ({"query_id": 1, "neighbor_count": 3}, {"query_id": 2, "neighbor_count": 0}))


if __name__ == "__main__":
    unittest.main()
