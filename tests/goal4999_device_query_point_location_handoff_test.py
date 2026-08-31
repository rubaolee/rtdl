from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Goal4999DeviceQueryPointLocationHandoffTest(unittest.TestCase):
    def test_public_wrapper_exposes_device_query_points(self) -> None:
        runtime = (ROOT / "src" / "rtdsl" / "optix_runtime.py").read_text(encoding="utf-8")
        wrapper_start = runtime.index("class PreparedOptixPlanarMapPointLocation2D:")
        wrapper_end = runtime.index("def prepare_planar_map_point_location_2d_optix", wrapper_start)
        wrapper = runtime[wrapper_start:wrapper_end]

        self.assertIn("def prepare_device_query_points(", wrapper)
        self.assertIn("self.prepared.prepare_device_query_points(", wrapper)
        self.assertIn("_with_env", wrapper)

    def test_native_device_query_point_abi_is_declared(self) -> None:
        prelude = (ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h").read_text(
            encoding="utf-8"
        )
        api = (ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp").read_text(
            encoding="utf-8"
        )
        workloads = (
            ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
        ).read_text(encoding="utf-8")

        self.assertIn("RtdlDirectedSegmentDeviceQueryPoint2D", prelude)
        self.assertIn(
            "rtdl_optix_prepare_directed_segment_point_location_device_query_points_2d",
            prelude,
        )
        self.assertIn(
            "rtdl_optix_prepare_directed_segment_point_location_device_query_points_2d",
            api,
        )
        self.assertIn("external_points_ptr", workloads)
        self.assertIn("points_device_ptr()", workloads)

    def test_rayjoin_app_uses_device_midpoint_query_points(self) -> None:
        app = (
            ROOT / "Paper-reproduction-apps" / "rayjoin-paper" / "section57_overlay_columnar_binary.py"
        ).read_text(encoding="utf-8")

        self.assertIn("DEVICE_QUERY_POINT_DTYPE", app)
        self.assertIn("def midpoint_query_points_device(", app)
        self.assertIn("_midpoint_device_query_points_kernel", app)
        self.assertIn("locator.prepare_device_query_points(", app)
        self.assertIn("midpoint_query_points_device_resident", app)
        self.assertIn("midpoint_query_points_host_pack_used", app)

    def test_writer_free_hot_accounting_includes_device_midpoint_query_points(self) -> None:
        app = (
            ROOT / "Paper-reproduction-apps" / "rayjoin-paper" / "section57_overlay_columnar_binary.py"
        ).read_text(encoding="utf-8")
        start = app.index("writer_free_hot_keys = [")
        end = app.index("lsi_phase_key = writer_free_hot_keys[0]", start)
        block = app[start:end]

        self.assertIn("midpoint_points_map0_device_query_points_sec", block)
        self.assertIn("midpoint_points_map1_device_query_points_sec", block)
        self.assertIn("if device_resident_carrier_enabled", block)


if __name__ == "__main__":
    unittest.main()
