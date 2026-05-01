import unittest

import rtdsl as rt
from examples import rtdl_road_hazard_screening as road_app
from examples import rtdl_segment_polygon_anyhit_rows as anyhit_app
from examples import rtdl_segment_polygon_hitcount as hitcount_app


DATASET = "authored_segment_polygon_minimal"


class Goal820SegmentPolygonRtCoreGateTest(unittest.TestCase):
    def test_segment_polygon_apps_have_goal941_prepared_rtx_gates(self) -> None:
        for app in ("road_hazard_screening", "segment_polygon_hitcount"):
            with self.subTest(app=app):
                self.assertEqual(
                    rt.optix_app_performance_support(app).performance_class,
                    "optix_traversal_prepared_summary",
                )
                self.assertEqual(rt.optix_app_benchmark_readiness(app).status, "ready_for_rtx_claim_review")
                self.assertEqual(rt.rt_core_app_maturity(app).current_status, "rt_core_ready")
        self.assertEqual(
            rt.optix_app_performance_support("segment_polygon_anyhit_rows").performance_class,
            "optix_traversal",
        )
        self.assertEqual(
            rt.optix_app_benchmark_readiness("segment_polygon_anyhit_rows").status,
            "ready_for_rtx_claim_review",
        )
        self.assertEqual(
            rt.rt_core_app_maturity("segment_polygon_anyhit_rows").current_status,
            "rt_core_ready",
        )

    def test_require_rt_core_rejects_optix_even_native_until_strict_gate_passes(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "strict RTX validation"):
            hitcount_app.run_case("optix", DATASET, optix_mode="native", require_rt_core=True)
        with self.assertRaisesRegex(RuntimeError, "requires --backend optix --output-mode rows --optix-mode native"):
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

    def test_anyhit_rows_require_rt_core_accepts_explicit_native_pair_row_path(self) -> None:
        rows = ({"segment_id": 1, "polygon_id": 10},)
        from unittest import mock

        with mock.patch.object(anyhit_app, "_run_native_anyhit_rows_optix", return_value=rows):
            payload = anyhit_app.run_case(
                "optix",
                DATASET,
                output_mode="rows",
                optix_mode="native",
                require_rt_core=True,
                output_capacity=16,
            )
        self.assertTrue(payload["rt_core_accelerated"])
        self.assertEqual(payload["rows"], rows)


if __name__ == "__main__":
    unittest.main()
