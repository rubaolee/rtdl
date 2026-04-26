from __future__ import annotations

import unittest
from unittest import mock

import rtdsl as rt
from examples import rtdl_segment_polygon_anyhit_rows as app


class Goal878SegmentPolygonNativePairRowsAppSurfaceTest(unittest.TestCase):
    def test_public_app_exposes_native_pair_rows_with_bounded_capacity(self) -> None:
        rows = (
            {"segment_id": 1, "polygon_id": 10},
            {"segment_id": 2, "polygon_id": 11},
        )
        with mock.patch.object(app, "_run_native_anyhit_rows_optix", return_value=rows) as native:
            payload = app.run_case(
                "optix",
                "authored_segment_polygon_minimal",
                output_mode="rows",
                optix_mode="native",
                output_capacity=32,
            )

        native.assert_called_once()
        self.assertEqual(payload["rows"], rows)
        self.assertEqual(payload["row_count"], 2)
        self.assertEqual(payload["summary_source"], "segment_polygon_anyhit_rows_native_bounded_optix")
        self.assertEqual(payload["native_output_capacity"], 32)
        self.assertTrue(payload["rt_core_accelerated"])

    def test_require_rt_core_is_narrow_to_native_rows_mode(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "requires --backend optix --output-mode rows --optix-mode native"):
            app.run_case(
                "optix",
                "authored_segment_polygon_minimal",
                output_mode="segment_counts",
                optix_mode="native",
                require_rt_core=True,
            )

    def test_optix_runtime_helper_rejects_invalid_capacity_before_backend_load(self) -> None:
        with self.assertRaisesRegex(ValueError, "output_capacity must be positive"):
            rt.segment_polygon_anyhit_rows_native_bounded_optix((), (), output_capacity=0)

    def test_matrix_records_partial_ready_real_artifact_gate(self) -> None:
        self.assertEqual(rt.app_engine_support_matrix()["segment_polygon_anyhit_rows"]["optix"].status, "direct_cli_native")
        self.assertEqual(
            rt.optix_app_benchmark_readiness("segment_polygon_anyhit_rows").status,
            "ready_for_rtx_claim_review",
        )
        self.assertEqual(
            rt.rt_core_app_maturity("segment_polygon_anyhit_rows").current_status,
            "rt_core_ready",
        )


if __name__ == "__main__":
    unittest.main()
