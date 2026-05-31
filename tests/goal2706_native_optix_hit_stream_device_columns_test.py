from pathlib import Path
import unittest

from rtdsl import optix_runtime


ROOT = Path(__file__).resolve().parents[1]
PRELUDE = ROOT / "src/native/optix/rtdl_optix_prelude.h"
CORE = ROOT / "src/native/optix/rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
API = ROOT / "src/native/optix/rtdl_optix_api.cpp"


class Goal2706NativeOptixHitStreamDeviceColumnsTest(unittest.TestCase):
    def test_native_abi_exports_device_columns_and_release_entrypoint(self) -> None:
        prelude = PRELUDE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")

        self.assertIn("struct RtdlNativeDeviceHitStreamColumns", prelude)
        self.assertIn("ray_ids_device_ptr", prelude)
        self.assertIn("primitive_ids_device_ptr", prelude)
        self.assertIn("owner_handle", prelude)
        self.assertIn("rtdl_optix_static_triangle_scene_3d_ray_triangle_hit_stream_device_columns", prelude)
        self.assertIn("rtdl_optix_release_ray_triangle_hit_stream_device_columns", prelude)
        self.assertIn('extern "C" int rtdl_optix_static_triangle_scene_3d_ray_triangle_hit_stream_device_columns', api)
        self.assertIn('extern "C" int rtdl_optix_release_ray_triangle_hit_stream_device_columns', api)

    def test_workload_path_writes_cuda_columns_without_host_row_download(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        core = CORE.read_text(encoding="utf-8")

        self.assertIn("g_raytriangle_hitstream_device_columns3d", core)
        self.assertIn("RayTriangleHitStreamDeviceColumns3DLaunchParams", workloads)
        self.assertIn("ray_triangle_hit_stream_device_columns_kernel_source_3d", workloads)
        self.assertIn("params.ray_ids[slot]", workloads)
        self.assertIn("params.primitive_ids[slot]", workloads)
        self.assertIn("NativeRayTriangleHitStreamDeviceColumnsOwner", workloads)
        self.assertIn("owner.release()", workloads)
        self.assertIn("release_ray_triangle_hit_stream_device_columns_optix", workloads)

        device_function = workloads[
            workloads.index("run_prepared_static_triangle_scene_3d_ray_triangle_hit_stream_device_columns_optix"):
            workloads.index("release_ray_triangle_hit_stream_device_columns_optix")
        ]
        self.assertNotIn("download(rows_out", device_function)
        self.assertNotIn("std::sort(rows_out", device_function)

    def test_python_runtime_binds_future_symbol_and_owner(self) -> None:
        self.assertEqual(
            optix_runtime.OPTIX_RAY_TRIANGLE_HIT_STREAM_3D_DEVICE_COLUMNS_SYMBOL,
            "rtdl_optix_static_triangle_scene_3d_ray_triangle_hit_stream_device_columns",
        )
        self.assertEqual(
            optix_runtime.OPTIX_RELEASE_RAY_TRIANGLE_HIT_STREAM_3D_DEVICE_COLUMNS_SYMBOL,
            "rtdl_optix_release_ray_triangle_hit_stream_device_columns",
        )
        self.assertTrue(hasattr(optix_runtime.PreparedOptixStaticTriangleScene3D, "ray_triangle_hit_stream_device_columns"))
        self.assertTrue(hasattr(optix_runtime, "ray_triangle_hit_stream_device_columns_3d_optix"))

        source = (ROOT / "src/rtdsl/optix_runtime.py").read_text(encoding="utf-8")
        self.assertIn("prepare_native_device_hit_stream_columns_from_abi", source)
        self.assertIn("_OptixNativeHitStreamDeviceColumnsOwner", source)
        self.assertIn("_RtdlNativeDeviceHitStreamColumns", source)
        self.assertIn("native_device_column_output_proven_on_hardware=True", source)
        self.assertIn("OPTIX_RELEASE_RAY_TRIANGLE_HIT_STREAM_3D_DEVICE_COLUMNS_SYMBOL", source)

    def test_new_native_surface_is_generic(self) -> None:
        text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (PRELUDE, CORE, WORKLOADS, API, ROOT / "src/rtdsl/optix_runtime.py")
        )
        new_markers = (
            "ray_triangle_hit_stream_device_columns",
            "RtdlNativeDeviceHitStreamColumns",
            "NativeRayTriangleHitStreamDeviceColumnsOwner",
        )
        snippets = "\n".join(line for line in text.splitlines() if any(marker in line for marker in new_markers))
        for forbidden in ("raydb", "sql", "database", "table", "dbscan", "hausdorff"):
            self.assertNotIn(forbidden, snippets.lower())


if __name__ == "__main__":
    unittest.main()
