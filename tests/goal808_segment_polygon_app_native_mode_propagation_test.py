from __future__ import annotations

import os
import unittest
from unittest import mock


class Goal808SegmentPolygonAppNativeModePropagationTest(unittest.TestCase):
    def test_road_hazard_native_mode_sets_env_for_optix_call(self) -> None:
        from examples import rtdl_road_hazard_screening as app

        observed: dict[str, str | None] = {}

        def fake_run_optix(kernel, **inputs):
            observed["mode"] = os.environ.get("RTDL_OPTIX_SEGPOLY_MODE")
            return ({"segment_id": 1, "hit_count": 2},)

        with mock.patch.object(app.rt, "run_optix", side_effect=fake_run_optix):
            payload = app.run_case("optix", output_mode="summary", optix_mode="native")

        self.assertEqual(observed["mode"], "native")
        self.assertEqual(payload["optix_mode"], "native")
        self.assertEqual(payload["priority_segment_count"], 1)

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

    def test_anyhit_pair_rows_reject_native_hitcount_mode(self) -> None:
        from examples import rtdl_segment_polygon_anyhit_rows as app

        with self.assertRaisesRegex(ValueError, "compact segment_flags or segment_counts"):
            app.run_case("optix", "authored_segment_polygon_minimal", "rows", "native")

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
