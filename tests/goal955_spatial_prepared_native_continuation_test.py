import sys
import unittest
from unittest import mock

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from examples import rtdl_event_hotspot_screening as hotspot
from examples import rtdl_facility_knn_assignment as facility
from examples import rtdl_service_coverage_gaps as coverage


class _FakePreparedFixedRadius:
    def __init__(self, rows):
        self.rows = tuple(rows)

    def run(self, query_points, *, radius, threshold=0):
        return self.rows

    def count_threshold_reached(self, query_points, *, radius, threshold=0):
        if threshold <= 0:
            return sum(1 for row in self.rows if int(row.get("neighbor_count", 0)) > 0)
        return sum(1 for row in self.rows if int(row.get("neighbor_count", 0)) >= threshold)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return None


def _coverage_rows(points):
    return tuple(
        {
            "query_id": point.id,
            "neighbor_count": 1,
            "threshold_reached": 1,
        }
        for point in points
    )


def _hotspot_rows(points):
    return tuple(
        {
            "query_id": point.id,
            "neighbor_count": 4 if point.id in {1, 2, 3, 4} else 1,
            "threshold_reached": 1,
        }
        for point in points
    )


class Goal955SpatialPreparedNativeContinuationTest(unittest.TestCase):
    def test_service_coverage_embree_gap_summary_reports_native_continuation(self) -> None:
        payload = coverage.run_case("embree", embree_summary_mode="gap_summary")

        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "embree_threshold_count")
        self.assertFalse(payload["rt_core_accelerated"])
        self.assertEqual(payload["rows"], [])

    def test_service_coverage_prepared_optix_reports_native_continuation(self) -> None:
        def fake_prepare(search_points, *, max_radius):
            return _FakePreparedFixedRadius(_coverage_rows(search_points))

        with mock.patch.object(coverage.rt, "prepare_optix_fixed_radius_count_threshold_2d", side_effect=fake_prepare):
            payload = coverage.run_case("optix", optix_summary_mode="gap_summary_prepared", require_rt_core=True)

        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "optix_threshold_count")
        self.assertTrue(payload["rt_core_accelerated"])
        self.assertEqual(payload["rows"], [])

    def test_event_hotspot_embree_count_summary_reports_native_continuation(self) -> None:
        payload = hotspot.run_case("embree", embree_summary_mode="count_summary")

        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "embree_threshold_count")
        self.assertFalse(payload["rt_core_accelerated"])
        self.assertEqual(payload["rows"], [])

    def test_event_hotspot_prepared_optix_reports_native_continuation(self) -> None:
        def fake_prepare(search_points, *, max_radius):
            return _FakePreparedFixedRadius(_hotspot_rows(search_points))

        with mock.patch.object(hotspot.rt, "prepare_optix_fixed_radius_count_threshold_2d", side_effect=fake_prepare):
            payload = hotspot.run_case("optix", optix_summary_mode="count_summary_prepared", require_rt_core=True)

        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "optix_threshold_count")
        self.assertTrue(payload["rt_core_accelerated"])
        self.assertEqual(payload["rows"], [])

    def test_facility_prepared_optix_coverage_reports_native_continuation(self) -> None:
        def fake_prepare(search_points, *, max_radius):
            return _FakePreparedFixedRadius(_coverage_rows(facility.make_facility_knn_case()["customers"]))

        with mock.patch.object(facility.rt, "prepare_optix_fixed_radius_count_threshold_2d", side_effect=fake_prepare):
            payload = facility.run_case("optix", optix_summary_mode="coverage_threshold_prepared", require_rt_core=True)

        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "optix_threshold_count")
        self.assertTrue(payload["rt_core_accelerated"])
        self.assertTrue(payload["matches_oracle"])

    def test_facility_knn_rows_do_not_report_native_continuation(self) -> None:
        payload = facility.run_case("cpu_python_reference", output_mode="summary")

        self.assertFalse(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "none")
        self.assertFalse(payload["rt_core_accelerated"])


if __name__ == "__main__":
    unittest.main()
