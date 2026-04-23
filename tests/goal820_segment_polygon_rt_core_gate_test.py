import unittest

import rtdsl as rt
from examples import rtdl_road_hazard_screening as road_app
from examples import rtdl_segment_polygon_anyhit_rows as anyhit_app
from examples import rtdl_segment_polygon_hitcount as hitcount_app


DATASET = "authored_segment_polygon_minimal"


class Goal820SegmentPolygonRtCoreGateTest(unittest.TestCase):
    def test_segment_polygon_apps_remain_native_tuning_candidates(self) -> None:
        for app in ("road_hazard_screening", "segment_polygon_hitcount", "segment_polygon_anyhit_rows"):
            with self.subTest(app=app):
                self.assertEqual(rt.optix_app_performance_support(app).performance_class, "host_indexed_fallback")
                self.assertEqual(rt.optix_app_benchmark_readiness(app).status, "needs_native_kernel_tuning")
                self.assertEqual(rt.rt_core_app_maturity(app).current_status, "needs_rt_core_redesign")

    def test_require_rt_core_rejects_optix_even_native_until_strict_gate_passes(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "strict RTX validation"):
            hitcount_app.run_case("optix", DATASET, optix_mode="native", require_rt_core=True)
        with self.assertRaisesRegex(RuntimeError, "strict RTX validation"):
            anyhit_app.run_case(
                "optix",
                DATASET,
                output_mode="segment_counts",
                optix_mode="native",
                require_rt_core=True,
            )
        with self.assertRaisesRegex(RuntimeError, "strict segment/polygon RTX validation"):
            road_app.run_case(
                "optix",
                output_mode="summary",
                optix_mode="native",
                require_rt_core=True,
            )

    def test_require_rt_core_is_optix_only(self) -> None:
        with self.assertRaisesRegex(ValueError, "only meaningful with --backend optix"):
            hitcount_app.run_case("embree", DATASET, require_rt_core=True)
        with self.assertRaisesRegex(ValueError, "only meaningful with --backend optix"):
            anyhit_app.run_case("embree", DATASET, require_rt_core=True)
        with self.assertRaisesRegex(ValueError, "only meaningful with --backend optix"):
            road_app.run_case("embree", require_rt_core=True)

    def test_cpu_payloads_record_no_rt_core_acceleration(self) -> None:
        self.assertFalse(hitcount_app.run_case("cpu_python_reference", DATASET)["rt_core_accelerated"])
        self.assertFalse(anyhit_app.run_case("cpu_python_reference", DATASET)["rt_core_accelerated"])
        self.assertFalse(road_app.run_case("cpu_python_reference")["rt_core_accelerated"])


if __name__ == "__main__":
    unittest.main()
