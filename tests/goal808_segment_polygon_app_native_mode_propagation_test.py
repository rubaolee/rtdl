from __future__ import annotations

import os
import unittest
from unittest import mock


class Goal808SegmentPolygonAppNativeModePropagationTest(unittest.TestCase):
    def test_road_hazard_native_mode_sets_env_for_optix_call(self) -> None:
        from examples import rtdl_road_hazard_screening as app

        prepared = mock.Mock()
        prepared.count_at_least.return_value = 1
        prepared.close.return_value = None

        with mock.patch.object(
            app.rt,
            "prepare_optix_segment_polygon_hitcount_2d",
            return_value=prepared,
        ) as prepare:
            payload = app.run_case("optix", output_mode="summary", optix_mode="native")

        prepare.assert_called_once()
        prepared.count_at_least.assert_called_once()
        prepared.close.assert_called_once()
        self.assertEqual(payload["optix_mode"], "native")
        self.assertEqual(payload["priority_segment_count"], 1)
        self.assertTrue(payload["native_continuation_active"])
        self.assertFalse(payload["summary_materializes_rows"])

    def test_anyhit_compact_mode_can_request_native_hitcount_path(self) -> None:
        from examples import rtdl_segment_polygon_anyhit_rows as app

        observed: dict[str, str | None] = {}

        def fake_run_optix(kernel, **inputs):
            observed["mode"] = os.environ.get("RTDL_OPTIX_SEGPOLY_MODE")
            return ({"segment_id": 1, "hit_count": 2},)

        with mock.patch.object(app.rt, "run_optix", side_effect=fake_run_optix):
            payload = app.run_case(
                "optix",
                "authored_segment_polygon_minimal",
                "segment_counts",
                "native",
            )

        self.assertEqual(observed["mode"], "native")
        self.assertEqual(payload["summary_source"], "segment_polygon_hitcount")
        self.assertEqual(payload["optix_mode"], "native")

    def test_anyhit_pair_rows_can_use_native_bounded_emitter(self) -> None:
        from examples import rtdl_segment_polygon_anyhit_rows as app

        with mock.patch.object(
            app,
            "_run_native_anyhit_rows_optix",
            return_value=({"segment_id": 1, "polygon_id": 10},),
        ) as native:
            payload = app.run_case("optix", "authored_segment_polygon_minimal", "rows", "native", output_capacity=16)

        native.assert_called_once()
        self.assertEqual(payload["summary_source"], "segment_polygon_anyhit_rows_native_bounded_optix")
        self.assertTrue(payload["rt_core_accelerated"])
        self.assertEqual(payload["native_output_capacity"], 16)

    def test_host_indexed_mode_restores_caller_env(self) -> None:
        from examples import rtdl_road_hazard_screening as app

        observed: dict[str, str | None] = {}

        def fake_run_optix(kernel, **inputs):
            observed["mode"] = os.environ.get("RTDL_OPTIX_SEGPOLY_MODE")
            return ()

        with mock.patch.dict(os.environ, {"RTDL_OPTIX_SEGPOLY_MODE": "native"}):
            with mock.patch.object(app.rt, "run_optix", side_effect=fake_run_optix):
                payload = app.run_case("optix", optix_mode="host_indexed")
            restored = os.environ.get("RTDL_OPTIX_SEGPOLY_MODE")

        self.assertIsNone(observed["mode"])
        self.assertEqual(restored, "native")
        self.assertEqual(payload["optix_mode"], "host_indexed")


if __name__ == "__main__":
    unittest.main()
