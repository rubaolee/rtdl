from __future__ import annotations

import os
import unittest
from unittest import mock


class Goal806SegmentPolygonOptixModeSurfaceTest(unittest.TestCase):
    def test_native_optix_mode_is_public_app_surface(self) -> None:
        from examples import rtdl_segment_polygon_hitcount as app

        observed: dict[str, str | None] = {}

        def fake_run_optix(kernel, **inputs):
            observed["mode"] = os.environ.get("RTDL_OPTIX_SEGPOLY_MODE")
            return ({"segment_id": 1, "hit_count": 2},)

        with mock.patch.object(app.rt, "run_optix", side_effect=fake_run_optix):
            payload = app.run_case(
                "optix",
                "authored_segment_polygon_minimal",
                optix_mode="native",
            )

        self.assertEqual(observed["mode"], "native")
        self.assertEqual(payload["optix_mode"], "native")
        self.assertEqual(payload["row_count"], 1)
        self.assertIn("experimental native", payload["boundary"])

    def test_host_indexed_mode_clears_env_temporarily_and_restores_it(self) -> None:
        from examples import rtdl_segment_polygon_hitcount as app

        observed: dict[str, str | None] = {}

        def fake_run_optix(kernel, **inputs):
            observed["mode"] = os.environ.get("RTDL_OPTIX_SEGPOLY_MODE")
            return ()

        with mock.patch.dict(os.environ, {"RTDL_OPTIX_SEGPOLY_MODE": "native"}):
            with mock.patch.object(app.rt, "run_optix", side_effect=fake_run_optix):
                payload = app.run_case(
                    "optix",
                    "authored_segment_polygon_minimal",
                    optix_mode="host_indexed",
                )
            restored = os.environ.get("RTDL_OPTIX_SEGPOLY_MODE")

        self.assertIsNone(observed["mode"])
        self.assertEqual(restored, "native")
        self.assertEqual(payload["optix_mode"], "host_indexed")


if __name__ == "__main__":
    unittest.main()
