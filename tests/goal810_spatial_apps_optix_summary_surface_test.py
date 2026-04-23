from __future__ import annotations

import unittest
from unittest import mock


class _PreparedCountStub:
    def __init__(self, rows):
        self.rows = tuple(rows)
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return None

    def run(self, query_points, *, radius: float, threshold: int):
        self.calls.append((tuple(query_points), radius, threshold))
        return self.rows


class Goal810SpatialAppsOptixSummarySurfaceTest(unittest.TestCase):
    def test_service_coverage_optix_prepared_gap_summary(self) -> None:
        from examples import rtdl_service_coverage_gaps as app

        rows = (
            {"query_id": 1, "neighbor_count": 1, "threshold_reached": 1},
            {"query_id": 2, "neighbor_count": 1, "threshold_reached": 1},
            {"query_id": 3, "neighbor_count": 1, "threshold_reached": 1},
            {"query_id": 4, "neighbor_count": 0, "threshold_reached": 0},
        )
        prepared = _PreparedCountStub(rows)

        with mock.patch.object(app.rt, "prepare_optix_fixed_radius_count_threshold_2d", return_value=prepared):
            payload = app.run_case("optix", optix_summary_mode="gap_summary_prepared")

        self.assertEqual(payload["backend"], "optix")
        self.assertEqual(payload["optix_summary_mode"], "gap_summary_prepared")
        self.assertEqual(payload["covered_household_count"], 3)
        self.assertEqual(payload["uncovered_household_ids"], [4])
        self.assertEqual(payload["rows"], [])
        self.assertEqual(prepared.calls[0][2], 1)

    def test_event_hotspot_optix_prepared_count_summary(self) -> None:
        from examples import rtdl_event_hotspot_screening as app

        rows = (
            {"query_id": 1, "neighbor_count": 4, "threshold_reached": 0},
            {"query_id": 2, "neighbor_count": 4, "threshold_reached": 0},
            {"query_id": 3, "neighbor_count": 4, "threshold_reached": 0},
            {"query_id": 4, "neighbor_count": 4, "threshold_reached": 0},
            {"query_id": 5, "neighbor_count": 1, "threshold_reached": 0},
            {"query_id": 6, "neighbor_count": 1, "threshold_reached": 0},
        )
        prepared = _PreparedCountStub(rows)

        with mock.patch.object(app.rt, "prepare_optix_fixed_radius_count_threshold_2d", return_value=prepared):
            payload = app.run_case("optix", optix_summary_mode="count_summary_prepared")

        self.assertEqual(payload["backend"], "optix")
        self.assertEqual(payload["optix_summary_mode"], "count_summary_prepared")
        self.assertEqual(payload["rows"], [])
        self.assertEqual(payload["neighbor_count_by_event"][1], 3)
        self.assertEqual([row["event_id"] for row in payload["hotspots"]], [1, 2, 3, 4])
        self.assertEqual(prepared.calls[0][2], 0)

    def test_service_and_event_reject_unknown_optix_summary_modes(self) -> None:
        from examples import rtdl_event_hotspot_screening
        from examples import rtdl_service_coverage_gaps

        with self.assertRaisesRegex(ValueError, "optix_summary_mode"):
            rtdl_service_coverage_gaps.run_case("optix", optix_summary_mode="bad")
        with self.assertRaisesRegex(ValueError, "optix_summary_mode"):
            rtdl_event_hotspot_screening.run_case("optix", optix_summary_mode="bad")


if __name__ == "__main__":
    unittest.main()
