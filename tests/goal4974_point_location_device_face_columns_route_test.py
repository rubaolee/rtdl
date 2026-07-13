from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "rayjoin-paper" / "section57_overlay_columnar_binary.py"


class Goal4974PointLocationDeviceFaceColumnsRouteTest(unittest.TestCase):
    def test_app_exposes_bounded_point_location_face_column_route(self) -> None:
        app = APP.read_text(encoding="utf-8")

        self.assertIn("--point-location-device-face-columns", app)
        self.assertIn("run_point_location_face_id_device_columns", app)
        self.assertIn("face_id_device_columns(", app)
        self.assertIn("device_column_row_buffer_from_point_location_id_columns", app)
        self.assertIn("point_location_device_face_columns_requested", app)
        self.assertIn("point_location_device_face_columns_downstream_numpy_copy_used", app)
        self.assertIn("point_location_device_face_columns_true_zero_copy_claim_authorized", app)

    def test_public_planar_map_point_location_wrapper_exposes_device_columns(self) -> None:
        runtime = (ROOT / "src" / "rtdsl" / "optix_runtime.py").read_text(encoding="utf-8")
        wrapper_start = runtime.index("class PreparedOptixPlanarMapPointLocation2D:")
        wrapper_end = runtime.index("def prepare_planar_map_point_location_2d_optix(", wrapper_start)
        wrapper = runtime[wrapper_start:wrapper_end]

        self.assertIn("def prepare_query_points(", wrapper)
        self.assertIn("def face_id_device_columns(", wrapper)
        self.assertIn("def segment_id_device_columns(", wrapper)
        self.assertIn("self._with_env(lambda: self.prepared.face_id_device_columns", wrapper)

    def test_route_reports_device_column_subphases_and_keeps_old_route_available(self) -> None:
        app = APP.read_text(encoding="utf-8")

        for key in (
            "_prepare_device_points_sec",
            "_face_id_device_columns_sec",
            "_face_id_device_columns_to_numpy_sec",
            "directed point-location face_id column",
        ):
            self.assertIn(key, app)

        self.assertIn("else base.run_point_location", app)
        self.assertIn("This is a measurement route, not a true-zero-copy claim", app)


if __name__ == "__main__":
    unittest.main()
