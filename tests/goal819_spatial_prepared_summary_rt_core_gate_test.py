import unittest

import rtdsl as rt
from examples import rtdl_event_hotspot_screening as event_app
from examples import rtdl_service_coverage_gaps as service_app


class Goal819SpatialPreparedSummaryRtCoreGateTest(unittest.TestCase):
    def test_spatial_apps_remain_partial_ready(self) -> None:
        expected = {
            "service_coverage_gaps": "gap_summary_prepared",
            "event_hotspot_screening": "count_summary_prepared",
        }
        for app, mode in expected.items():
            with self.subTest(app=app):
                self.assertEqual(
                    rt.optix_app_performance_support(app).performance_class,
                    "optix_traversal_prepared_summary",
                )
                self.assertEqual(rt.optix_app_benchmark_readiness(app).status, "needs_phase_contract")
                self.assertEqual(rt.rt_core_app_maturity(app).current_status, "rt_core_partial_ready")
                self.assertIn(mode, rt.optix_app_performance_support(app).note)

    def test_require_rt_core_rejects_non_optix_backends(self) -> None:
        with self.assertRaisesRegex(ValueError, "only meaningful with --backend optix"):
            service_app.run_case("embree", embree_summary_mode="gap_summary", require_rt_core=True)
        with self.assertRaisesRegex(ValueError, "only meaningful with --backend optix"):
            event_app.run_case("embree", embree_summary_mode="count_summary", require_rt_core=True)

    def test_require_rt_core_rejects_optix_row_modes_before_optix_dispatch(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "requires --optix-summary-mode gap_summary_prepared"):
            service_app.run_case("optix", optix_summary_mode="rows", require_rt_core=True)
        with self.assertRaisesRegex(RuntimeError, "requires --optix-summary-mode count_summary_prepared"):
            event_app.run_case("optix", optix_summary_mode="rows", require_rt_core=True)

    def test_cpu_payloads_record_no_rt_core_acceleration(self) -> None:
        service_payload = service_app.run_case("cpu_python_reference")
        event_payload = event_app.run_case("cpu_python_reference")
        self.assertFalse(service_payload["rt_core_accelerated"])
        self.assertFalse(event_payload["rt_core_accelerated"])
        self.assertEqual(service_payload["optix_performance"]["class"], "optix_traversal_prepared_summary")
        self.assertEqual(event_payload["optix_performance"]["class"], "optix_traversal_prepared_summary")


if __name__ == "__main__":
    unittest.main()
