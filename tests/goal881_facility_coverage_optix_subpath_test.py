from __future__ import annotations

import unittest
from unittest import mock

from examples import rtdl_facility_knn_assignment as app


class _PreparedCoverageThreshold:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def run(self, customers, *, radius: float, threshold: int):
        self.customer_count = len(customers)
        self.radius = radius
        self.threshold = threshold
        return tuple(
            {
                "query_id": customer.id,
                "neighbor_count": 1,
                "threshold_reached": 1,
            }
            for customer in customers
        )


class Goal881FacilityCoverageOptixSubpathTest(unittest.TestCase):
    def test_optix_coverage_threshold_mode_uses_prepared_traversal(self) -> None:
        prepared = _PreparedCoverageThreshold()
        with mock.patch.object(app.rt, "prepare_optix_fixed_radius_count_threshold_2d", return_value=prepared) as mocked:
            payload = app.run_case(
                "optix",
                optix_summary_mode="coverage_threshold_prepared",
                service_radius=1.0,
                require_rt_core=True,
            )

        mocked.assert_called_once()
        self.assertEqual(prepared.customer_count, payload["customer_count"])
        self.assertEqual(prepared.radius, 1.0)
        self.assertEqual(prepared.threshold, 1)
        self.assertTrue(payload["rt_core_accelerated"])
        self.assertTrue(payload["coverage_threshold"]["all_customers_covered"])
        self.assertTrue(payload["matches_oracle"])
        self.assertIn("facility-coverage decision", payload["rtdl_role"])
        self.assertIn("not nearest-depot ranking", payload["boundary"])

    def test_optix_default_rows_mode_rejected(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "coverage_threshold_prepared"):
            app.run_case("optix")

    def test_require_rt_core_rejects_non_optix_backend(self) -> None:
        with self.assertRaisesRegex(ValueError, "--require-rt-core"):
            app.run_case("embree", require_rt_core=True)

    def test_negative_service_radius_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "service_radius must be non-negative"):
            app.run_case("optix", optix_summary_mode="coverage_threshold_prepared", service_radius=-0.1)
        case = app.make_facility_knn_case()
        with self.assertRaisesRegex(ValueError, "radius must be non-negative"):
            app.facility_coverage_oracle(case["customers"], case["depots"], radius=-0.1)

    def test_grid_oracle_matches_expected_scaled_fixture(self) -> None:
        case = app.make_facility_knn_case(copies=200)
        summary = app.facility_coverage_oracle(case["customers"], case["depots"], radius=1.0)

        self.assertTrue(summary["all_customers_covered"])
        self.assertEqual(summary["customer_count"], 800)
        self.assertEqual(summary["covered_customer_count"], 800)
        self.assertEqual(summary["uncovered_customer_ids"], [])

    def test_zero_radius_oracle_requires_exact_coordinate_match(self) -> None:
        customers = (app.rt.Point(id=1, x=0.0, y=0.0), app.rt.Point(id=2, x=1.0, y=0.0))
        depots = (app.rt.Point(id=10, x=0.0, y=0.0),)

        summary = app.facility_coverage_oracle(customers, depots, radius=0.0)

        self.assertFalse(summary["all_customers_covered"])
        self.assertEqual(summary["covered_customer_count"], 1)
        self.assertEqual(summary["uncovered_customer_ids"], [2])

    def test_missing_rows_are_uncovered(self) -> None:
        case = app.make_facility_knn_case()
        rows = (
            {"query_id": 1, "neighbor_count": 1, "threshold_reached": 1},
        )

        summary = app._coverage_threshold_from_count_rows(
            rows,
            customers=case["customers"],
            radius=1.0,
        )

        self.assertFalse(summary["all_customers_covered"])
        self.assertEqual(summary["uncovered_customer_ids"], [2, 3, 4])
        self.assertEqual(summary["covered_customer_count"], 1)


if __name__ == "__main__":
    unittest.main()
