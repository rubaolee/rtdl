from __future__ import annotations

import unittest
from unittest import mock

from examples import rtdl_ann_candidate_app as ann
from examples import rtdl_facility_knn_assignment as facility


class Goal1300V15AnnFacilityGenericMigrationTest(unittest.TestCase):
    def test_ann_candidate_threshold_uses_generic_prepared_wrapper(self) -> None:
        with mock.patch.object(
            ann.rt,
            "run_generic_prepared_fixed_radius_threshold_reached_count_2d",
            return_value={
                "primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
                "summary_primitive": "REDUCE_INT(COUNT)",
                "threshold_reached_count": 3,
            },
        ) as generic_count:
            payload = ann.run_app(
                "optix",
                optix_summary_mode="candidate_threshold_prepared",
                candidate_radius=0.2,
                require_rt_core=True,
            )

        generic_count.assert_called_once()
        _, kwargs = generic_count.call_args
        self.assertEqual(kwargs["backend"], "optix")
        self.assertEqual(kwargs["radius"], 0.2)
        self.assertEqual(kwargs["threshold"], 1)
        self.assertEqual(payload["candidate_threshold"]["generic_primitive"], "FIXED_RADIUS_COUNT_THRESHOLD_2D")
        self.assertTrue(payload["candidate_threshold"]["within_candidate_radius"])
        self.assertTrue(payload["rt_core_accelerated"])

    def test_facility_coverage_threshold_uses_generic_prepared_wrapper(self) -> None:
        with mock.patch.object(
            facility.rt,
            "run_generic_prepared_fixed_radius_threshold_reached_count_2d",
            return_value={
                "primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
                "summary_primitive": "REDUCE_INT(COUNT)",
                "threshold_reached_count": 4,
            },
        ) as generic_count:
            payload = facility.run_case(
                "optix",
                optix_summary_mode="coverage_threshold_prepared",
                service_radius=1.0,
                require_rt_core=True,
            )

        generic_count.assert_called_once()
        _, kwargs = generic_count.call_args
        self.assertEqual(kwargs["backend"], "optix")
        self.assertEqual(kwargs["radius"], 1.0)
        self.assertEqual(kwargs["threshold"], 1)
        self.assertEqual(payload["coverage_threshold"]["generic_primitive"], "FIXED_RADIUS_COUNT_THRESHOLD_2D")
        self.assertTrue(payload["coverage_threshold"]["all_customers_covered"])
        self.assertTrue(payload["rt_core_accelerated"])


if __name__ == "__main__":
    unittest.main()
